"""FastAPI Router for Agentic RAG Chatbot API."""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException

from app.models.schemas import ChatRequest
from app.services.chat_service import process_chat
from app.services.ingestion_service import run_ingestion_background
from app.storage.vector_store import clear_vector_store
from app.core.dependencies import (
    get_lazy_vector_store,
    get_lazy_reranker,
    clear_global_store,
)
from app.services.s3_service import upload_file_to_s3

logger = logging.getLogger(__name__)

api_router = APIRouter()


@api_router.post("/api/chat")
async def chat_endpoint(body: ChatRequest) -> Dict[str, Any]:
    """Handle user queries and generate answers via the agentic RAG pipeline."""
    try:
        vector_store = get_lazy_vector_store()
        reranker = get_lazy_reranker()

        return process_chat(
            query=body.query,
            chat_history=body.chat_history,
            vector_store=vector_store,
            reranker=reranker,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/api/upload")
async def upload_document(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
) -> Dict[str, Any]:
    """Upload documents to S3 and kick off background ingestion.

    Ingestion runs asynchronously via FastAPI BackgroundTasks — the response
    returns immediately while processing continues in the background.
    """
    saved_filenames = []
    allowed_extensions = (".pdf", ".docx", ".txt")

    for uploaded_file in files:
        if not uploaded_file.filename.lower().endswith(allowed_extensions):
            continue

        file_bytes = await uploaded_file.read()
        s3_url = upload_file_to_s3(file_bytes, uploaded_file.filename)
        logger.info(f"Uploaded {uploaded_file.filename} to S3 at {s3_url}")
        saved_filenames.append(uploaded_file.filename)

    if not saved_filenames:
        raise HTTPException(
            status_code=400,
            detail="No valid files provided. Allowed: PDF, DOCX, TXT.",
        )

    background_tasks.add_task(run_ingestion_background, saved_filenames)

    return {
        "message": "Upload successful. Ingestion is running in the background.",
        "files_processed": saved_filenames,
    }


@api_router.post("/api/clear")
async def clear_kb() -> Dict[str, str]:
    """Clear the Pinecone knowledge base."""
    try:
        vector_store = get_lazy_vector_store()
        if vector_store is not None:
            clear_vector_store(vector_store)

        clear_global_store()
        get_lazy_vector_store()  # trigger reload

        return {"message": "Knowledge Base cleared successfully."}
    except Exception as e:
        logger.error(f"Clear KB error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/api/health")
async def health_check() -> Dict[str, Any]:
    """Return the current health and readiness status of the API."""
    from app.core.dependencies import _embedding_model, _vector_store
    return {
        "status": "healthy",
        "models_loaded": _embedding_model is not None,
        "kb_ready": _vector_store is not None,
    }
