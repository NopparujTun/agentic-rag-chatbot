"""FastAPI Router for Enterprise Smart KB API."""

import logging
import os
import shutil
import tempfile
from typing import List, Dict, Any

from fastapi import APIRouter, Request, UploadFile, File, HTTPException, Depends

from app.models.schemas import ChatRequest
from app.services.chat_service import process_chat
from app.services.ingestion_service import run_ingestion_pipeline
from app.storage.vector_store import clear_hybrid_store
from app.core.config import load_config
from app.core.dependencies import (
    get_lazy_embedding_model,
    get_lazy_hybrid_store,
    get_lazy_reranker,
    clear_global_store,
    get_current_tenant_id
)
from app.services.s3_service import upload_file_to_s3, delete_s3_bucket_contents
from app.api.auth import router as auth_router

logger = logging.getLogger(__name__)

api_router = APIRouter()
api_router.include_router(auth_router)
app_config = load_config()


@api_router.post("/api/chat")
async def chat_endpoint(request: Request, body: ChatRequest, tenant_id: str = Depends(get_current_tenant_id)) -> Dict[str, Any]:
    """Endpoint to handle user queries and generate answers."""
    try:
        vector_store, bm25_retriever = get_lazy_hybrid_store()
        reranker = get_lazy_reranker()
        
        return process_chat(
            query=body.query,
            chat_history=body.chat_history,
            vector_store=vector_store,
            bm25_retriever=bm25_retriever,
            reranker=reranker,
            tenant_id=tenant_id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.post("/api/upload")
async def upload_document(request: Request, files: List[UploadFile] = File(...), tenant_id: str = Depends(get_current_tenant_id)) -> Dict[str, Any]:
    """Endpoint to handle document uploads and trigger asynchronous ingestion."""
    from app.tasks import ingest_documents_task
    
    saved_filenames = []
    allowed_extensions = (".pdf", ".docx", ".txt")
    
    for uploaded_file in files:
        if not uploaded_file.filename.lower().endswith(allowed_extensions):
            continue
            
        file_bytes = await uploaded_file.read()
        
        # Upload to S3
        s3_url = upload_file_to_s3(file_bytes, uploaded_file.filename)
        logger.info(f"Uploaded {uploaded_file.filename} to S3 at {s3_url}")
        
        saved_filenames.append(uploaded_file.filename)
        
    if not saved_filenames:
        raise HTTPException(status_code=400, detail="No valid files provided. Allowed: PDF, DOCX, TXT.")
        
    try:
        # Trigger Celery Task
        task = ingest_documents_task.delay(saved_filenames, tenant_id)
        
        return {
            "message": "Ingestion started",
            "task_id": task.id,
            "files_processed": saved_filenames
        }
    except Exception as e:
        logger.error(f"Failed to start ingestion task: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to start ingestion task: {str(e)}")


@api_router.get("/api/tasks/{task_id}")
async def get_task_status(task_id: str, tenant_id: str = Depends(get_current_tenant_id)) -> Dict[str, Any]:
    """Endpoint to check the status of a Celery task."""
    from app.core.celery_app import celery_app
    from celery.result import AsyncResult
    
    task_result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    
    if task_result.status == "SUCCESS":
        response["result"] = task_result.result
        # Reload lazy stores on success
        clear_global_store()
    elif task_result.status == "FAILURE":
        response["error"] = str(task_result.result)
        
    return response


@api_router.post("/api/clear")
async def clear_kb(request: Request, tenant_id: str = Depends(get_current_tenant_id)) -> Dict[str, str]:
    """Endpoint to clear the knowledge base."""
    try:
        vector_store, bm25_retriever = get_lazy_hybrid_store()
        if vector_store is not None:
            clear_hybrid_store(vector_store, app_config["vector_db"]["persist_directory"], tenant_id=tenant_id)
            
        # Optional: We could also scope S3 deletions to tenant if needed
        # For now, just keep S3 delete globally or scoped if needed.
        # delete_s3_bucket_contents()
            
        clear_global_store()
        get_lazy_hybrid_store() # trigger reload
        
        return {"message": "Knowledge Base cleared successfully."}
    except Exception as e:
        logger.error(f"Clear KB error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/api/health")
async def health_check(request: Request) -> Dict[str, Any]:
    """Endpoint to check the health status of the API."""
    from app.core.dependencies import _embedding_model, _vector_store
    return {
        "status": "healthy",
        "models_loaded": _embedding_model is not None,
        "kb_ready": _vector_store is not None
    }
