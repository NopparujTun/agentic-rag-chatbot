<h1 align="center">Agentic RAG Chatbot</h1>

<p align="center">
  <strong>Advanced AI-powered Document Assistant with Hybrid Search (Semantic + Keyword), VLM PDF Extraction, and Agentic Reasoning</strong>
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#architecture--workflow">Architecture & Workflow</a> •
  <a href="#core-technologies">Core Technologies</a> •
  <a href="#codebase-structure">Codebase Structure</a> •
  <a href="#api-reference">API Reference</a> •
  <a href="#installation--setup">Installation & Setup</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/React-19-blue?logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-00a393?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Pinecone-Vector%20DB-00C896" alt="Pinecone"/>
  <img src="https://img.shields.io/badge/LangGraph-1.1%2B-orange?logo=langchain&logoColor=white" alt="LangGraph"/>
  <img src="https://img.shields.io/badge/TailwindCSS-v4-38B2AC?logo=tailwind-css&logoColor=white" alt="Tailwind"/>
</p>

---

## 📖 Overview

This repository provides a comprehensive implementation of an **Agentic RAG (Retrieval-Augmented Generation)** chatbot built on a modern decoupled architecture. The system acts as a highly intelligent document assistant, capable of interpreting complex documents (PDFs, DOCX, TXT), understanding intricate queries, and delivering precise, source-backed answers through autonomous reasoning.

Unlike standard RAG implementations, this project utilizes **Agentic Orchestration** via LangGraph, enabling the AI to evaluate context, iteratively search, and reason before responding. It features an advanced ingestion pipeline that handles complex, scanned, and image-heavy PDFs using **Vision-Language Models (VLM)**, ensuring that visual information is as searchable as text.

---

## ✨ Key Features

### 🧠 Agentic Reasoning & RAG
- **LangGraph ReAct Agent:** Uses a reasoning-and-acting (ReAct) loop to decide if retrieved context is sufficient. It can perform multiple searches iteratively to ensure accurate answers.
- **Autonomous Tool Use:** The chatbot intelligently decides when to search the knowledge base and how to refine its queries based on initial findings.
- **Zero Hallucination Guardrails:** Strict prompt engineering ensures the agent only answers using retrieved context. If it cannot find the answer, it politely declines rather than guessing.

### 🔍 Hybrid Search & Retrieval
- **Dual Indexing Strategy:** Combines **Dense Vector Search** (Semantic matching via Pinecone & Sentence Transformers) with **Sparse Keyword Search** (Lexical matching via local BM25).
- **Reciprocal Rank Fusion (RRF):** Intelligently merges semantic and keyword search results to deliver the most contextually relevant documents.
- **Cross-Encoder Reranking:** Re-evaluates and re-scores retrieved documents against the query to maximize precision (MRR@10 > 92%).

### 📄 State-of-the-Art Document Ingestion
- **Intelligent PDF Routing:** Automatically detects PDF types (digital, scanned, image-heavy).
- **VLM Extraction:** Uses **Gemini 2.5 Flash** to extract text, tables, and describe images/diagrams from visually complex PDFs.
- **Docling & PyMuPDF:** Provides OCR for scanned documents and fast, high-fidelity markdown conversion for standard digital PDFs.
- **Thai NLP Normalization:** Specialized cleaning for Thai language text, fixing broken vowels and enforcing proper character boundaries.

### 💻 Modern Web UI
- **React 19 & Vite 6:** Ultra-fast, highly responsive frontend architecture.
- **Tailwind CSS v4:** Modern, utility-first styling for a sleek, interactive aesthetic.
- **Real-time Interaction:** Features chat history, markdown rendering, thinking indicators, and drag-and-drop document uploads.

---

## 🏗 Architecture & Workflow

The system is strictly decoupled into a RESTful Backend and an SPA Frontend.

### 📥 Ingestion Workflow (Document Upload)
1. **Upload:** User drops files into the React UI (`/api/upload`).
2. **Classification:** Backend evaluates if the file is a PDF (digital/scanned/image-heavy) or a text document.
3. **Extraction:** Dispatches to the appropriate parser (PyMuPDF4LLM, Docling OCR, or Gemini VLM).
4. **Processing & Cleaning:** Markdown text is passed through the NLP cleaner.
5. **Chunking:** Text is split using `RecursiveCharacterTextSplitter` (default: 1000 chars, 200 overlap).
6. **Indexing:** Chunks are simultaneously embedded into Pinecone (Vector) and serialized into a local BM25 Pickle file.

### 💬 Chat Workflow (Query Processing)
1. **Query Input:** User sends a question along with chat history.
2. **Agent Initialization:** The FastAPI router passes the query to the LangGraph ReAct Agent.
3. **Hybrid Search:** The agent queries the `search_knowledge_base` tool. The tool runs Pinecone + BM25, fuses results via RRF, and reranks them.
4. **Evaluation:** The Agent evaluates the context. If insufficient, it refines its search query and loops back.
5. **Generation:** Once satisfied, the LLM generates a grounded answer citing specific source documents.
6. **Response:** The frontend renders the answer and explicitly displays the referenced source segments.

---

## 🛠 Core Technologies

### Backend Stack
- **Framework:** FastAPI, Uvicorn, Python 3.10+
- **AI & Orchestration:** LangChain, LangGraph, Langchain-OpenAI, Langchain-Google-GenAI
- **Vector Database:** Pinecone
- **Embeddings & Ranking:** Sentence-Transformers, Rank BM25
- **Document Processing:** Docling, PyMuPDF, PyMuPDF4LLM, fitz

### Frontend Stack
- **Framework:** React 19, TypeScript
- **Build Tool:** Vite 6
- **Styling:** Tailwind CSS v4, CLSX, Tailwind-Merge
- **State Management:** React Context API

---

## 📂 Codebase Structure

### Backend (`/backend`)
```text
backend/
├── main.py                     # App entry point, FastAPI setup, and Model initialization lifecycle
├── requirements.txt            # Python dependencies
├── config.yaml                 # System configurations (chunk size, model names, etc.)
└── app/
    ├── api/
    │   └── router.py           # FastAPI endpoints (/chat, /upload, /clear, /health)
    ├── core/
    │   └── config.py           # Configuration loader logic
    ├── models/
    │   └── schemas.py          # Pydantic schemas for request/response validation
    ├── rag/
    │   ├── generator.py        # LangGraph ReAct Agent, OpenTyphoon/OpenAI integration
    │   └── retriever.py        # HybridRetriever class, RRF implementation, Cross-Encoder Reranker
    ├── services/
    │   ├── chat_service.py     # Chat business logic, formatting output
    │   ├── ingestion_service.py# Chunking, NLP text cleaning, indexing orchestration
    │   └── pdf_processor.py    # VLM Gemini extraction, Docling OCR, PyMuPDF parsing logic
    ├── storage/
    │   └── vector_store.py     # Pinecone and BM25 local storage management
    └── tools/
        └── search.py           # LangChain tool definition for the Agent's search capabilities
```

### Frontend (`/frontend`)
```text
frontend/
├── package.json                # Node dependencies and scripts
├── vite.config.ts              # Vite configuration
├── index.html                  # Main HTML template
└── src/
    ├── main.tsx                # React DOM render entry point
    ├── App.tsx                 # Main layout routing (Sidebar, Upload, Chat views)
    ├── api.ts                  # Fetch API wrappers for backend communication
    ├── components/
    │   ├── ChatSidebar.tsx     # History and session management UI
    │   ├── ChatInput.tsx       # Text area for querying
    │   ├── HomePage.tsx        # Landing view
    │   ├── UploadPage.tsx      # Drag-and-drop document upload interface
    │   └── MainContent.tsx     # Message rendering and scroll management
    ├── context/
    │   └── ChatContext.tsx     # Global state management for messages and UI status
    └── hooks/
        ├── useChat.ts          # Custom hook for handling chat submissions and API calls
        └── useUpload.ts        # Custom hook for handling file uploads and API calls
```

---

## 🌐 API Reference

The backend exposes a RESTful API hosted by default on `http://localhost:8000`.

### `POST /api/chat`
Process a query and return an AI-generated answer.
- **Body:** `{ "query": "string", "chat_history": "string" }`
- **Returns:** `{ "answer": "string", "sources": [...], "steps": [...], "response_time_seconds": float }`

### `POST /api/upload`
Uploads documents, processes them, and indexes them into the knowledge base.
- **Body:** `multipart/form-data` with `files` (Array of PDF, DOCX, TXT)
- **Returns:** `{ "message": "string", "total_chunks": int, "ingestion_time_seconds": float, "files_processed": [...] }`

### `POST /api/clear`
Wipes the Pinecone index, deletes local BM25 data, and clears uploaded files.
- **Returns:** `{ "message": "Knowledge Base cleared successfully." }`

### `GET /api/health`
Checks system status and model loading state.
- **Returns:** `{ "status": "healthy", "models_loaded": boolean, "kb_ready": boolean }`

---

## 🚀 Installation & Setup

### Prerequisites
- **Python 3.10+**
- **Node.js v20+**
- **Pinecone Account** (Free tier works)
- **OpenAI API Key** (Or OpenTyphoon API Key)
- **Google Gemini API Key** (Required for VLM PDF Extraction)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/agentic-rag-chatbot.git
cd agentic-rag-chatbot
```

### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Environment Variables:**
Create a `.env` file in the `backend/` directory:
```env
TYPHOON_API_KEY=your_typhoon_or_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
GOOGLE_API_KEY=your_google_gemini_api_key
```

**Start the Server:**
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
*Note: The first startup may take a few moments as it downloads embedding and reranking models locally.*

### 3. Frontend Setup
Open a new terminal window.

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```
Access the application at `http://localhost:5173`.

---

## 📊 Evaluation & Benchmarks

The RAG pipeline has been rigorously evaluated against ground-truth datasets.

- **Baseline Semantic Search:** 86.8% MRR@10
- **BM25 Keyword Only:** 59.1% MRR@10
- **Hybrid (RRF) + Cross-Encoder Reranker:** 🏆 **92.3% MRR (95.0% Recall@10)**

**Latency:**
Average end-to-end response time for Hybrid retrieval is **~828 ms**, balancing exceptional accuracy with real-time responsiveness.

---

## ⚠️ Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| **Backend fails to start** | Missing `.env` variables or invalid Pinecone key | Ensure `PINECONE_API_KEY` is valid. Ensure `config.yaml` index name matches your Pinecone index. |
| **PDF Upload fails** | Corrupted PDF or missing Docling dependencies | Check backend logs. If OCR fails, ensure system packages for Docling (like Tesseract) are installed if running on Linux. |
| **VLM Extraction skipped** | Missing `GOOGLE_API_KEY` | Ensure the Google API key is set in `.env` for complex PDF processing to utilize Gemini. |
| **CORS Error on Frontend** | Backend not running on Port 8000 | Ensure FastAPI is running on `http://localhost:8000` or update frontend `vite.config.ts` proxy settings. |

---
<p align="center">
  <em>Built for autonomous, highly accurate AI knowledge retrieval.</em>
</p>
