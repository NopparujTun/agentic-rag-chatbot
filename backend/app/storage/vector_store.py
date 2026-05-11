"""Pinecone vector store operations."""

import logging
from typing import List

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore

logger = logging.getLogger(__name__)


def save_vector_store(
    chunks: List[Document],
    embedding_model: Embeddings,
    index_name: str,
) -> PineconeVectorStore:
    """Index document chunks into Pinecone."""
    logger.info("Uploading %d chunks to Pinecone index '%s'", len(chunks), index_name)
    return PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        index_name=index_name,
    )


def load_vector_store(
    embedding_model: Embeddings,
    index_name: str,
) -> PineconeVectorStore:
    """Connect to an existing Pinecone index."""
    logger.info("Connecting to Pinecone index '%s'", index_name)
    return PineconeVectorStore(
        index_name=index_name,
        embedding=embedding_model,
    )


def clear_vector_store(vectorstore: PineconeVectorStore) -> None:
    """Clear all vectors from Pinecone."""
    logger.info("Clearing Pinecone knowledge base.")
    try:
        vectorstore.delete(delete_all=True)
        logger.info("Deleted all vectors from Pinecone.")
    except Exception as exc:
        logger.error("Failed to delete from Pinecone: %s", exc)
