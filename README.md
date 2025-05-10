# SmartGrid AI

SmartGrid AI is a spreadsheet-like web application that allows users to enrich structured data (like student info, leads, etc.) with AI-powered columns using LLMs (OpenAI GPT). No coding required—just type, click, and get insights!

---

## Features
- Spreadsheet UI: Add, edit, delete rows and columns
- AI Columns: Enrich data with AI (classification, extraction, etc.)
- Regenerate AI results per row
- Save/load sheets (localStorage)
- Export to CSV
- Multiple sheet templates (e.g., Student Info, Leads)
- FastAPI backend with OpenAI integration

---

## Tech Stack
- **Frontend:** React (Next.js), TailwindCSS, TypeScript
- **Backend:** FastAPI (Python), OpenAI API

---

## Getting Started

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd smart-grid-ai
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/` with your OpenAI API key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

Start the backend:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd ../  # Project root
npm install  # or pnpm install
npm run dev  # or pnpm dev
```

Visit [http://localhost:3000/app](http://localhost:3000/app) in your browser.

---

## Usage
- Click **Add AI Column** to create a new AI-powered column.
- Enter a prompt (e.g., "Classify this major as Engineer or Non-Engineer").
- Click **Regenerate** to update AI results for a row after editing.
- Click **Export** to download the current sheet as CSV.

---

## API Endpoints
- `POST /api/enrich` — Enrich a single row with AI
- `POST /api/enrich/batch` — Enrich multiple rows at once

---

## License
MIT 