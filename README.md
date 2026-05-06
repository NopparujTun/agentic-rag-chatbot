<p align="center">
  <img alt="Enterprise Smart Knowledge-Base Logo" src="frontend/public/logo.svg" width="350px">
</p>

<h1 align="center">Enterprise Smart Knowledge-Base</h1>

<p align="center">
  <strong>AI-powered document assistant with Hybrid Search (Semantic + Keyword)</strong>
  </p>

  <p align="center">
  <a href="#overview">Overview</a> •
  <a href="#how-it-works">How It Works</a> •
  <a href="#core-technologies">Core Technologies</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#installation--usage">Installation & Usage</a> •
  <a href="#troubleshooting">Troubleshooting</a>
  </p>

  <p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/React-19-blue?logo=react&logoColor=white" alt="React"/>
  <img src="https://img.shields.io/badge/FastAPI-0.100%2B-00a393?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Pinecone-Vector%20DB-00C896" alt="Pinecone"/>
  <img src="https://img.shields.io/badge/LangGraph-1.1%2B-orange?logo=langchain&logoColor=white" alt="LangGraph"/>
  </p>

  <p align="center">
  <strong>If you like this project, a star ⭐️ would mean a lot :)</strong><br>
  </p>

  ## Overview

  This repository demonstrates how to build an **Agentic RAG (Retrieval-Augmented Generation)** application using a modern decoupled architecture. It features a React (TypeScript) frontend and a FastAPI (Python) backend.

  Most RAG tutorials show basic concepts but lack guidance on building modular, agent-driven systems — this project bridges that gap by providing **both a high-performance web UI and an extensible backend architecture**.

  ### What's inside

  | Feature | Description |
  |---|---|
  | 🗂️ **Advanced Document Processing** | Utilizes Docling and PyMuPDF for high-fidelity text extraction from complex PDFs |
  | 🧠 **Thai Language NLP Pipeline** | Built-in support for Thai language tokenization, broken vowel fixes, and boundary normalization via PyThaiNLP |
  | ❓ **Hybrid Search Strategy** | Blends dense vector search (semantic) via Pinecone with sparse keyword search (BM25) using Reciprocal Rank Fusion (RRF) |
  | 🤖 **Agentic Orchestration** | LangChain and LangGraph route queries, retrieve context, and evaluate document relevance before answering |
  | 🔍 **Modern UI/UX** | Snappy, real-time React 19 frontend stylized with Tailwind CSS v4 |

  ### 🎯 Two Parts of This Repo

  **1️⃣ Backend (`/backend`)**

  A robust REST API built with FastAPI. It handles complex document ingestion, Thai NLP preprocessing, Hybrid Search, and LangGraph orchestration.

  **2️⃣ Frontend (`/frontend`)**

  A modern web UI built with React 19, TypeScript, Vite, and Tailwind CSS v4. It features a responsive chat interface, a document upload portal, and real-time streaming responses.

  ## How It Works

  ### Document Preparation: Hybrid Indexing

  Before queries can be processed, documents are ingested and split for optimal retrieval.
  The system automatically extracts text and cleans it using PyThaiNLP. Chunks are embedded with local embedding models and stored in Pinecone (vectors) + a local BM25 index (keywords).

  ### Query Processing: Intelligent Workflow
  ```
  User Query → Hybrid Search (Semantic + BM25) → RRF Retrieval →
  Agent Evaluation & Context Aggregation → OpenTyphoon LLM Synthesis → Final Response
  ```

  **Stage 1 — Intelligent Retrieval:** The system performs a Hybrid Search, combining semantic vector search with keyword-based retrieval using Reciprocal Rank Fusion to deliver highly relevant results.

  **Stage 2 — Response Generation:** The LLM generates a grounded answer based on the aggregated context and prior chat history.

  ---
## Core Technologies

This system is built using the latest modern stacks:

### Backend Stack
- **FastAPI / Uvicorn**: High-performance REST API
- **LangChain / LangGraph**: Agent orchestration and query routing
- **Pinecone**: Vector database for dense embeddings
- **Rank BM25**: Sparse keyword retrieval
- **Sentence Transformers**: Local embedding generation
- **PyThaiNLP**: Advanced Thai text processing
- **Docling & PyMuPDF**: PDF parsing and extraction

### Frontend Stack
- **React 19**: Modern UI rendering
- **Vite 6**: Fast development build tool
- **Tailwind CSS v4**: Utility-first styling
- **TypeScript**: Strict type checking

---

## Architecture

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

## Installation & Usage

### 1. Backend Setup (FastAPI)

Ensure you have **Python 3.10+** installed.

```bash
# Navigate to backend
cd backend

# Create and activate a virtual environment
python -m venv venv
source venv/bin/activate  # Or `venv\Scripts\activate` on Windows

# Install packages
pip install -r requirements.txt
```

**Environment Configuration:**
Create a `.env` file in the `backend/` directory:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
```

**Run the Server:**
```bash
uvicorn api:app --reload --port 8000
```

### 2. Frontend Setup (React)

Ensure you have **Node.js (v20+)** installed.

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run the development server
npm run dev
```

The frontend will be available at `http://localhost:5173`. Open this URL in your browser to start chatting and uploading documents.

---

## Troubleshooting

| Area | Common Problems | Suggested Solutions |
|------|----------------|------------------|
| **Model Selection** | - Poor context understanding | - Ensure `TYPHOON_API_KEY` is correctly set and valid. |
| **Retrieval Configuration** | - Relevant documents not retrieved | - Verify `PINECONE_API_KEY` and check that the index dimension matches the embedding model. |
| **PDF Ingestion** | - Text extraction fails or gives garbled output | - Complex PDFs might require Docling configuration tweaks; check the `backend/config.yaml`. |
| **Frontend Connection** | - Network Error / CORS Issues | - Ensure the backend is running on `http://localhost:8000`. |
