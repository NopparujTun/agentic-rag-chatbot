"""FastAPI Router for Agentic RAG Chatbot API."""

import logging
from typing import List, Dict, Any

from fastapi import APIRouter, BackgroundTasks, UploadFile, File, HTTPException, Depends

from app.models.schemas import ChatRequest
from app.services.chat_service import answer_query
from app.services.ingestion_service import run_ingestion_background
from app.services.document_store import DocumentStore, get_document_store
from app.core.dependencies import Resources, get_resources

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = (".pdf", ".docx", ".txt")
ERROR_NO_VALID_FILES = "No valid files provided. Supported formats: PDF, DOCX, TXT."

api_router = APIRouter()


@api_router.post("/api/chat")
async def chat_endpoint(
    body: ChatRequest,
    resources: Resources = Depends(get_resources),
) -> Dict[str, Any]:
    """Handle user queries and generate answers via the agentic RAG pipeline."""
    try:
        return answer_query(
            query=body.query,
            chat_history=body.chat_history,
            vector_store=resources.vector_store(),
            reranker=resources.reranker(),
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
    store: DocumentStore = Depends(get_document_store),
) -> Dict[str, Any]:
    """Upload documents to the document store and kick off background ingestion.

    Ingestion runs asynchronously via FastAPI BackgroundTasks — the response
    returns immediately while processing continues in the background.
    """
    saved_filenames = []

    for uploaded_file in files:
        if not uploaded_file.filename.lower().endswith(ALLOWED_EXTENSIONS):
            continue

        file_bytes = await uploaded_file.read()
        locator = store.put(uploaded_file.filename, file_bytes)
        logger.info(f"Uploaded {uploaded_file.filename} to {locator}")
        saved_filenames.append(uploaded_file.filename)

    if not saved_filenames:
        raise HTTPException(
            status_code=400,
            detail=ERROR_NO_VALID_FILES,
        )

    background_tasks.add_task(run_ingestion_background, saved_filenames)

    return {
        "message": "Upload successful. Ingestion is running in the background.",
        "files_processed": saved_filenames,
    }


@api_router.post("/api/clear")
async def clear_kb(
    resources: Resources = Depends(get_resources),
) -> Dict[str, str]:
    """Clear the Pinecone knowledge base."""
    try:
        resources.clear_knowledge_base()
        return {"message": "Knowledge Base cleared successfully."}
    except Exception as e:
        logger.error(f"Clear KB error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/api/health")
async def health_check(
    resources: Resources = Depends(get_resources),
) -> Dict[str, Any]:
    """Return the current health and readiness status of the API."""
    return {"status": "healthy", **resources.status()}
