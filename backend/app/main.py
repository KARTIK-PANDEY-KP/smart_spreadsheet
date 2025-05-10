from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import os
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential
import openai
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://100.64.195.143:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Check if API key is set
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logger.error("OPENAI_API_KEY environment variable is not set")
    raise ValueError("OPENAI_API_KEY environment variable is not set")
else:
    logger.info("OPENAI_API_KEY is set (length: %d)", len(api_key))

# Initialize OpenAI client
openai_client = openai.AsyncOpenAI(api_key=api_key)

class EnrichmentRequest(BaseModel):
    rowData: Dict[str, str]
    prompt: str
    columnName: str

class EnrichmentResponse(BaseModel):
    result: str
    confidence: Optional[float] = None
    processingTime: Optional[float] = None

class BatchEnrichmentRequest(BaseModel):
    rows: List[Dict[str, Any]]
    prompt: str
    columnName: str

class BatchEnrichmentResponse(BaseModel):
    results: List[Dict[str, Any]]
    processingTime: Optional[float] = None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_ai_completion(prompt: str) -> str:
    try:
        logger.info("Attempting to get AI completion for prompt: %s", prompt[:50] + "...")
        response = await openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a data analysis assistant. Provide concise answers and exactly what "
                        "the user asks for. For example, if user says add a value to a column then "
                        "only add the value and print the value with no additional information or "
                        "English. Simply analyze the query and identify what the user is asking since "
                        "it's a column for a spreadsheet assume what forms of simplification you may "
                        "have to do. IF THE RELEVANT DATA NEEDED FOR MAKING THE VALUE IS NOT PRESENT "
                        "DON'T ASSUME AND KEEP IT EMPTY. Keep the output fact checked, only use what "
                        "is in the input. For example, if asked to extract company from email "
                        "'john@acme.com', only extract 'acme' without adding corp/com/co/llc etc."
                    )
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=50
        )
        result = response.choices[0].message.content.strip()
        logger.info("Successfully got AI completion")
        return result
    except Exception as e:
        logger.error("Unexpected Error: %s", str(e))
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/api/enrich", response_model=EnrichmentResponse)
async def enrich_data(request: EnrichmentRequest):
    start_time = time.time()
    try:
        # Format the prompt with the row data
        formatted_prompt = f"{request.prompt}\n\nData:\n"
        for key, value in request.rowData.items():
            formatted_prompt += f"{key}: {value}\n"
        
        # Get AI completion
        result = await get_ai_completion(formatted_prompt)
        
        processing_time = time.time() - start_time
        
        return EnrichmentResponse(
            result=result,
            confidence=0.95,  # Mock confidence score
            processingTime=processing_time
        )
    
    except Exception as e:
        logger.error("Error in enrich_data: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enrich/batch", response_model=BatchEnrichmentResponse)
async def enrich_batch(request: BatchEnrichmentRequest):
    start_time = time.time()
    try:
        results = []
        
        for row in request.rows:
            # Format the prompt with the row data
            formatted_prompt = f"{request.prompt}\n\nData:\n"
            for key, value in row["data"].items():
                formatted_prompt += f"{key}: {value}\n"
            
            # Get AI completion
            result = await get_ai_completion(formatted_prompt)
            
            results.append({
                "rowId": row["rowId"],
                "result": result
            })
        
        processing_time = time.time() - start_time
        
        return BatchEnrichmentResponse(
            results=results,
            processingTime=processing_time
        )
    
    except Exception as e:
        logger.error("Error in enrich_batch: %s", str(e))
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 