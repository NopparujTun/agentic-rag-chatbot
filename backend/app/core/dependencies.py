"""Dependencies for FastAPI endpoints."""

import logging
from typing import Tuple, Optional, Any

from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore
from sentence_transformers import CrossEncoder

from app.core.config import load_config
from app.rag.retriever import get_embedding_model, get_reranker
from app.storage.vector_store import load_hybrid_store

logger = logging.getLogger(__name__)
app_config = load_config()

# Global state for lazy loading
_embedding_model: Optional[Embeddings] = None
_vector_store: Optional[PineconeVectorStore] = None
_bm25_retriever: Optional[Any] = None
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


def get_lazy_hybrid_store() -> Tuple[PineconeVectorStore, Any]:
    global _vector_store, _bm25_retriever
    if _vector_store is None or _bm25_retriever is None:
        logger.info("Lazy loading hybrid store...")
        embedding_model = get_lazy_embedding_model()
        _vector_store, _bm25_retriever = load_hybrid_store(
            embedding_model=embedding_model,
            persist_dir=app_config["vector_db"]["persist_directory"],
            index_name=app_config["vector_db"]["index_name"],
        )
    return _vector_store, _bm25_retriever


def get_lazy_reranker() -> CrossEncoder:
    global _reranker
    if _reranker is None:
        logger.info("Lazy loading reranker...")
        _reranker = get_reranker()
    return _reranker

def clear_global_store():
    global _vector_store, _bm25_retriever
    _vector_store = None
    _bm25_retriever = None
