"""Main application entry point for Enterprise Smart KB API."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv

from app.api.router import api_router
from app.core.config import load_config
from app.rag.retriever import get_embedding_model, get_reranker
from app.storage.vector_store import load_hybrid_store

load_dotenv()
logger = logging.getLogger(__name__)

app_config = load_config()

@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    """Load and cache all heavy models on application startup."""
    logger.info("Loading embedding model...")
    fastapi_app.state.embedding_model = get_embedding_model(
        app_config["embedding"]["model_name"],
        app_config["embedding"]["device"],
    )
    
    logger.info("Loading hybrid store...")
    fastapi_app.state.vector_store, fastapi_app.state.bm25_retriever = load_hybrid_store(
        embedding_model=fastapi_app.state.embedding_model,
        persist_dir=app_config["vector_db"]["persist_directory"],
        index_name=app_config["vector_db"]["index_name"],
    )
    
    logger.info("Loading reranker...")
    fastapi_app.state.reranker = get_reranker()
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

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
