# Agentic RAG Chatbot

An Agentic RAG chatbot that uses a LangGraph ReAct agent to perform hybrid search (Pinecone vector + local BM25) and VLM-based PDF extraction.

## Tech Stack

- **Backend:** FastAPI, Python 3.10+, LangGraph, LangChain, Pinecone
- **Frontend:** React 19, Vite 6, Tailwind CSS v4
- **Document Processing:** Docling, PyMuPDF, Gemini VLM

## Setup

### Prerequisites
- Python 3.10+
- Node.js v20+
- API Keys: Pinecone, OpenAI (or Typhoon), Google Gemini

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create `backend/.env`:
```env
TYPHOON_API_KEY=your_api_key
PINECONE_API_KEY=your_pinecone_key
GOOGLE_API_KEY=your_gemini_key
```

Run backend:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
The app will be available at `http://localhost:5173`.

### 3. Docker (Alternative)
```bash
docker-compose up --build -d
```

## API

- `POST /api/chat`: Process query
- `POST /api/upload`: Upload documents (PDF, DOCX, TXT)
- `POST /api/clear`: Clear knowledge base
- `GET /api/health`: Health check
