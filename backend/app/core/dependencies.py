"""Application resources: the lazily-loaded models and vector store, behind one interface.

A single ``Resources`` instance owns the embedding model, the reranker, and the
vector store. Heavy models load on first access and are cached. ``reset()`` drops
the cached vector store so the next access reloads it; ``clear_knowledge_base()``
additionally wipes the Pinecone index. ``status()`` reports readiness without
forcing a load. Endpoints receive it via ``Depends(get_resources)``; the
background ingestion task imports the singleton directly.
"""

import logging
from typing import Dict, Optional

from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore, PineconeEmbeddings
from sentence_transformers import CrossEncoder

from app.core.config import load_config
from app.storage.vector_store import load_vector_store, clear_vector_store

logger = logging.getLogger(__name__)


class Resources:
    """Owns the lazily-loaded embedding model, reranker, and vector store."""

    def __init__(self) -> None:
        self._config = load_config()
        self._embedding_model: Optional[Embeddings] = None
        self._vector_store: Optional[PineconeVectorStore] = None
        self._reranker: Optional[CrossEncoder] = None

    def embedding_model(self) -> Embeddings:
        if self._embedding_model is None:
            logger.info("Lazy loading embedding model...")
            self._embedding_model = PineconeEmbeddings(
                model=self._config["embedding"]["model_name"],
            )
        return self._embedding_model

    def vector_store(self) -> PineconeVectorStore:
        if self._vector_store is None:
            logger.info("Lazy loading vector store...")
            self._vector_store = load_vector_store(
                embedding_model=self.embedding_model(),
                index_name=self._config["vector_db"]["index_name"],
            )
        return self._vector_store

    def reranker(self) -> CrossEncoder:
        if self._reranker is None:
            logger.info("Lazy loading reranker...")
            self._reranker = CrossEncoder(
                "BAAI/bge-reranker-v2-m3", max_length=512, device="cpu",
            )
        return self._reranker

    def reset(self) -> None:
        """Drop the cached vector store so the next access reloads it."""
        self._vector_store = None

    def clear_knowledge_base(self) -> None:
        """Wipe the Pinecone index, then drop the cache so it reloads empty."""
        clear_vector_store(self.vector_store())
        self.reset()

    def status(self) -> Dict[str, bool]:
        """Report readiness without forcing a load."""
        return {
            "models_loaded": self._embedding_model is not None,
            "kb_ready": self._vector_store is not None,
        }


resources = Resources()


def get_resources() -> Resources:
    return resources
