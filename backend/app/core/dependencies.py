"""Dependencies for FastAPI endpoints."""

import logging
from typing import Optional

from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore
from sentence_transformers import CrossEncoder

from app.core.config import load_config
from app.rag.retriever import get_embedding_model, get_reranker
from app.storage.vector_store import load_vector_store

logger = logging.getLogger(__name__)
app_config = load_config()

# Global state for lazy loading
_embedding_model: Optional[Embeddings] = None
_vector_store: Optional[PineconeVectorStore] = None
_reranker: Optional[CrossEncoder] = None


def get_lazy_embedding_model() -> Embeddings:
    global _embedding_model
    if _embedding_model is None:
        logger.info("Lazy loading embedding model...")
        _embedding_model = get_embedding_model(
            app_config["embedding"]["model_name"],
            app_config["embedding"]["device"],
        )
    return _embedding_model


def get_lazy_vector_store() -> PineconeVectorStore:
    global _vector_store
    if _vector_store is None:
        logger.info("Lazy loading vector store...")
        embedding_model = get_lazy_embedding_model()
        _vector_store = load_vector_store(
            embedding_model=embedding_model,
            index_name=app_config["vector_db"]["index_name"],
        )
    return _vector_store


def get_lazy_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        logger.info("Lazy loading reranker...")
        _reranker = get_reranker()
    return _reranker


def clear_global_store():
    global _vector_store
    _vector_store = None
