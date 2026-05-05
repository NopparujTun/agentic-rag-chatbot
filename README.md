# Agentic RAG Chatbot

![Agentic RAG](frontend/public/logo.svg) 

**Agentic RAG Chatbot** is an advanced, production-ready Retrieval-Augmented Generation system. It features a modern decoupled architecture with a **React (TypeScript)** frontend and a **FastAPI (Python)** backend. The system enables users to upload PDF documents, automatically ingest and chunk them into a searchable knowledge base, and ask questions in natural language. 

By leveraging **Hybrid Search**—combining semantic vector search (Pinecone) with keyword-based retrieval (BM25) and Reciprocal Rank Fusion (RRF)—the application delivers highly relevant and grounded answers.

---

## 🏗️ Architecture Overview

The system is separated into three main parts:

1. **Frontend (`/frontend`)**: A modern web UI built with React 19, TypeScript, Vite, and Tailwind CSS v4. It features a responsive chat interface, a document upload portal, and real-time streaming responses.
2. **Backend (`/backend`)**: A robust REST API built with FastAPI. It handles complex document ingestion (via `docling`, `pymupdf4llm`), LangChain/LangGraph orchestration, Thai NLP preprocessing (via `pythainlp`), and Hybrid Search.
3. **Research Notebooks (`/notebook`)**: Jupyter notebooks (`agentic_rag.ipynb`, `smart_pdf_conversion.ipynb`) for testing RAG chunking strategies, document conversion accuracy, and embedding models.

```text
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend (Vite)                     │
│              Chat UI  ·  Document Upload                    │
└────────────────────────┬────────────────────────────────────┘
                         │ (REST API / JSON / Multipart)
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
   ┌─────────────┐ ┌──────────┐ ┌─────────────┐
   │  Ingestion  │ │   RAG    │ │   FastAPI   │
   │   Pipeline  │ │  Engine  │ │   Server    │
   └──────┬──────┘ └────┬─────┘ └─────────────┘
          │             │              
          ▼             ▼              
   ┌─────────────┐ ┌──────────┐ 
   │ Docling +   │ │  Hybrid  │ 
   │ Thai NLP    │ │  Search  │ 
   └─────────────┘ └────┬─────┘ 
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       ┌─────────────┐     ┌──────────────┐
       │   Pinecone  │     │  Local BM25  │
       │  (Vectors)  │     │  (Pickle)    │
       └─────────────┘     └──────────────┘
```

---

## 🌟 Key Features

- **Advanced Document Processing**: Utilizes `docling` and `PyMuPDF` for high-fidelity text extraction from complex PDFs.
- **Thai Language NLP Pipeline**: Built-in support for Thai language tokenization, broken vowel fixes, and boundary normalization via `pythainlp`.
- **Hybrid Search Strategy**: Blends dense vector search (semantic) via Pinecone with sparse keyword search (BM25) for unparalleled retrieval accuracy.
- **Agentic Orchestration**: Uses `LangChain` and `LangGraph` to route queries, retrieve context, and evaluate document relevance before answering.
- **Modern UI/UX**: Snappy, real-time React 19 frontend stylized with Tailwind CSS v4.

---

## 📁 Directory Structure

```text
agentic-rag-chatbot/
├── backend/                  # FastAPI Application
│   ├── src/                  # Core RAG, Ingestion, and Utils logic
│   ├── local_bm25_data/      # BM25 Keyword Search Indices
│   ├── uploaded_docs/        # Temporary storage for uploaded documents
│   ├── api.py                # FastAPI server and endpoints
│   ├── config.yaml           # Chunking and Vector DB configurations
│   └── requirements.txt      # Python dependencies
│
├── frontend/                 # React UI Application
│   ├── src/                  # React Components, Hooks, and API calls
│   ├── public/               # Static assets
│   ├── package.json          # Node dependencies
│   ├── vite.config.ts        # Vite configuration
│   └── eslint.config.js      # Strict TypeScript linting rules
│
├── notebook/                 # Research & Prototyping
│   ├── agentic_rag.ipynb     # Pipeline experimentations
│   └── smart_pdf_conversion.ipynb
│
├── README.md                 # This file
└── .gitignore                # Root gitignore rules
```

---

## 🚀 Getting Started

### 1. Backend Setup

Ensure you have **Python 3.10+** installed.

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows

pip install -r requirements.txt
```

**Environment Variables**:
Create a `.env` file in the `backend/` directory:
```env
# Example configuration
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

**Run the Server**:
```bash
uvicorn api:app --reload --port 8000
```

### 2. Frontend Setup

Ensure you have **Node.js** (v20+) installed.

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:5173`.

---

## ⚙️ Configuration Reference

The behavior of the RAG pipeline is controlled by `backend/config.yaml`:

```yaml
ingestion:
  chunk_size: 1000
  chunk_overlap: 200
  
embedding:
  model_name: "llama-text-embed-v2"
  device: "cpu"

vector_db:
  persist_directory: "./local_bm25_data"
  index_name: "main"
```

---

## 🛠️ Tech Stack Details

**Frontend**:
- React 19
- Vite 6
- Tailwind CSS v4
- TypeScript

**Backend**:
- FastAPI & Uvicorn
- LangChain & LangGraph
- Pinecone (Vector Database)
- Sentence Transformers
- Rank BM25
- PyThaiNLP
- Docling & PyMuPDF (PDF Parsing)