"""FastAPI Router for Enterprise Smart KB API."""

import logging
import os
import shutil
from typing import List, Dict, Any

from fastapi import APIRouter, Request, UploadFile, File, HTTPException

from app.models.schemas import ChatRequest
from app.services.chat_service import process_chat
from app.services.ingestion_service import run_ingestion_pipeline
from app.storage.vector_store import clear_hybrid_store, load_hybrid_store
from app.core.config import load_config

logger = logging.getLogger(__name__)

api_router = APIRouter()
app_config = load_config()
UPLOAD_DIRECTORY = os.path.abspath(app_config.get("upload_dir", "uploaded_docs"))


@api_router.post("/api/chat")
async def chat_endpoint(request: Request, body: ChatRequest) -> Dict[str, Any]:
    """Endpoint to handle user queries and generate answers."""
    try:
        return process_chat(
            query=body.query,
            chat_history=body.chat_history,
            vector_store=request.app.state.vector_store,
            bm25_retriever=request.app.state.bm25_retriever,
            reranker=request.app.state.reranker
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/api/upload")
async def upload_document(request: Request, files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    """Endpoint to handle document uploads and trigger ingestion."""
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
            embedding_model=request.app.state.embedding_model,
            index_name=app_config["vector_db"]["index_name"],
            persist_dir=app_config["vector_db"]["persist_directory"],
            chunk_size=app_config["ingestion"]["chunk_size"],
            chunk_overlap=app_config["ingestion"]["chunk_overlap"]
        )
        
        request.app.state.vector_store = new_vector_store
        request.app.state.bm25_retriever = new_bm25_retriever
        
        return {
            "message": "Ingestion successful",
            "total_chunks": total_indexed_chunks,
            "ingestion_time_seconds": round(ingestion_time, 2),
            "files_processed": [os.path.basename(path) for path in saved_file_paths]
        }
    except Exception as e:
        logger.error(f"Ingestion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")


@api_router.post("/api/clear")
async def clear_kb(request: Request) -> Dict[str, str]:
    """Endpoint to clear the knowledge base."""
    try:
        if request.app.state.vector_store is not None:
            clear_hybrid_store(request.app.state.vector_store, app_config["vector_db"]["persist_directory"])
            
        if os.path.exists(UPLOAD_DIRECTORY):
            shutil.rmtree(UPLOAD_DIRECTORY)
            os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)
            
        request.app.state.vector_store, request.app.state.bm25_retriever = load_hybrid_store(
            embedding_model=request.app.state.embedding_model,
            persist_dir=app_config["vector_db"]["persist_directory"],
            index_name=app_config["vector_db"]["index_name"],
        )
        
        return {"message": "Knowledge Base cleared successfully."}
    except Exception as e:
        logger.error(f"Clear KB error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/api/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """Endpoint to check the health status of the API."""
    return {
        "status": "healthy",
        "models_loaded": request.app.state.embedding_model is not None,
        "kb_ready": request.app.state.vector_store is not None
    }
