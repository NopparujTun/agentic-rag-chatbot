"""Enterprise Smart Knowledge Base API Layer.

This module exposes the REST API endpoints for chatting, uploading documents,
and managing the vector store. Business logic is delegated to service functions.
"""

import logging
import os
import shutil
import time
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

from src.ingestion.ingestion import run_ingestion_pipeline
from src.rag.retrieval import get_embedding_model, load_hybrid_store, clear_hybrid_store, get_reranker
from src.rag.generator import generate_answer
from src.utils.config import load_config

load_dotenv()
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Initialization
# ---------------------------------------------------------------------------

app_config = load_config()
UPLOAD_DIRECTORY = os.path.abspath(app_config.get("upload_dir", "uploaded_docs"))

# Global variables for models
global_embedding_model = None
global_vector_store = None
global_bm25_retriever = None
global_reranker = None

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Load and cache all heavy models on application startup."""
    global global_embedding_model, global_vector_store, global_bm25_retriever, global_reranker
    
    logger.info("Loading embedding model...")
    global_embedding_model = get_embedding_model(
        app_config["embedding"]["model_name"],
        app_config["embedding"]["device"],
    )
    
    logger.info("Loading hybrid store...")
    global_vector_store, global_bm25_retriever = load_hybrid_store(
        embedding_model=global_embedding_model,
        persist_dir=app_config["vector_db"]["persist_directory"],
        index_name=app_config["vector_db"]["index_name"],
    )
    
    logger.info("Loading reranker...")
    global_reranker = get_reranker()
    logger.info("Models loaded successfully.")
    yield


app = FastAPI(title="Enterprise Smart KB API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------

class ChatRequest(BaseModel):
    """Data model for a chat request."""
    query: str
    chat_history: str = ""


# ---------------------------------------------------------------------------
# Service Functions
# ---------------------------------------------------------------------------

def _process_chat(request: ChatRequest) -> Dict[str, Any]:
    """Encapsulates the business logic for the chat endpoint."""
    if global_vector_store is None:
        raise HTTPException(status_code=400, detail="Database not initialized. Please upload files first.")
         
    try:
        start_time = time.time()
        answer, retrieved_sources, steps_taken = generate_answer(
            query=request.query,
            vectorstore=global_vector_store,
            bm25_retriever=global_bm25_retriever,
            chat_history=request.chat_history,
            reranker=global_reranker
        )
        response_time = time.time() - start_time
        
        serialized_sources = [
            {
                "content": doc.page_content,
                "metadata": doc.metadata
            }
            for doc in retrieved_sources
        ] if retrieved_sources else []
        
        serialized_steps = [
            {
                "tool": action.tool,
                "tool_input": action.tool_input,
                "observation": observation
            }
            for action, observation in steps_taken
        ] if steps_taken else []
        
        return {
            "answer": answer,
            "sources": serialized_sources,
            "steps": serialized_steps,
            "response_time_seconds": round(response_time, 2)
        }
    except Exception as exception:
        logger.error(f"Chat error: {exception}")
        raise HTTPException(status_code=500, detail=str(exception))


def _process_upload(files: List[UploadFile]) -> Dict[str, Any]:
    """Encapsulates the business logic for the file upload endpoint."""
    global global_vector_store, global_bm25_retriever
    os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
    
    saved_file_paths = []
    allowed_extensions = (".pdf", ".docx", ".txt")
    
    for uploaded_file in files:
        if not uploaded_file.filename.lower().endswith(allowed_extensions):
            continue
        
        file_location = os.path.join(UPLOAD_DIRECTORY, uploaded_file.filename)
        with open(file_location, "wb+") as file_object:
            shutil.copyfileobj(uploaded_file.file, file_object)
        saved_file_paths.append(file_location)
        
    if not saved_file_paths:
        raise HTTPException(status_code=400, detail="No valid files provided. Allowed: PDF, DOCX, TXT.")
        
    try:
        new_vector_store, new_bm25_retriever, total_indexed_chunks, ingestion_time = run_ingestion_pipeline(
            file_paths=saved_file_paths,
            embedding_model=global_embedding_model,
            index_name=app_config["vector_db"]["index_name"],
            persist_dir=app_config["vector_db"]["persist_directory"],
            chunk_size=app_config["ingestion"]["chunk_size"],
            chunk_overlap=app_config["ingestion"]["chunk_overlap"]
        )
        
        global_vector_store = new_vector_store
        global_bm25_retriever = new_bm25_retriever
        
        return {
            "message": "Ingestion successful",
            "total_chunks": total_indexed_chunks,
            "ingestion_time_seconds": round(ingestion_time, 2),
            "files_processed": [os.path.basename(path) for path in saved_file_paths]
        }
    except Exception as exception:
        logger.error(f"Ingestion failed: {exception}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(exception)}")


def _process_clear() -> Dict[str, str]:
    """Encapsulates the business logic to clear the vector database."""
    global global_vector_store, global_bm25_retriever
    
    try:
        if global_vector_store is not None:
            clear_hybrid_store(global_vector_store, app_config["vector_db"]["persist_directory"])
            
        if os.path.exists(UPLOAD_DIRECTORY):
            shutil.rmtree(UPLOAD_DIRECTORY)
            os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
            
        global_vector_store, global_bm25_retriever = load_hybrid_store(
            embedding_model=global_embedding_model,
            persist_dir=app_config["vector_db"]["persist_directory"],
            index_name=app_config["vector_db"]["index_name"],
        )
        
        return {"message": "Knowledge Base cleared successfully."}
    except Exception as exception:
        logger.error(f"Clear KB error: {exception}")
        raise HTTPException(status_code=500, detail=str(exception))


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest) -> Dict[str, Any]:
    """Endpoint to handle user queries and generate answers.

    Args:
        request: The incoming chat request.

    Returns:
        A dictionary containing the generated answer, sources, and steps.
    """
    return _process_chat(request)


@app.post("/api/upload")
async def upload_document(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    """Endpoint to handle document uploads and trigger ingestion.

    Args:
        files: A list of uploaded files.

    Returns:
        A dictionary detailing ingestion statistics.
    """
    return _process_upload(files)


@app.post("/api/clear")
async def clear_kb() -> Dict[str, str]:
    """Endpoint to clear the knowledge base.

    Returns:
        A success message indicating the vector store has been cleared.
    """
    return _process_clear()


@app.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Endpoint to check the health status of the API.

    Returns:
        A dictionary showing the health status and model availability.
    """
    return {
        "status": "healthy",
        "models_loaded": global_embedding_model is not None,
        "kb_ready": global_vector_store is not None
    }


if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
