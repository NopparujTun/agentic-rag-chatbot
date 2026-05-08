"""Storage operations for vector and keyword databases."""

import logging
import os
import pickle
import shutil
from typing import List, Tuple, Optional

from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore

logger = logging.getLogger(__name__)

BM25_FILENAME = "bm25_index.pkl"


def save_hybrid_store(
    chunks: List[Document],
    embedding_model: Embeddings,
    persist_dir: str,
    index_name: str,
) -> Tuple[PineconeVectorStore, BM25Retriever]:
    """Index document chunks into Pinecone and save a local BM25 index."""
    os.makedirs(persist_dir, exist_ok=True)

    logger.info("Uploading %d chunks to Pinecone index '%s'", len(chunks), index_name)
    vector_store = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embedding_model,
        index_name=index_name,
    )

    bm25_retriever = BM25Retriever.from_documents(chunks)
    bm25_file_path = os.path.join(persist_dir, BM25_FILENAME)
    
    with open(bm25_file_path, "wb") as file_handle:
        pickle.dump(bm25_retriever, file_handle)

    logger.info("Saved BM25 index to %s", bm25_file_path)
    return vector_store, bm25_retriever


def load_hybrid_store(
    embedding_model: Embeddings,
    persist_dir: str,
    index_name: str,
) -> Tuple[PineconeVectorStore, Optional[BM25Retriever]]:
    """Connect to an existing Pinecone index and load the local BM25 index."""
    logger.info("Connecting to Pinecone index '%s'", index_name)
    vector_store = PineconeVectorStore(
        index_name=index_name,
        embedding=embedding_model,
    )

    bm25_file_path = os.path.join(persist_dir, BM25_FILENAME)
    bm25_retriever = None
    
    if os.path.exists(bm25_file_path):
        with open(bm25_file_path, "rb") as file_handle:
            bm25_retriever = pickle.load(file_handle)
        logger.info("Loaded BM25 index from %s", bm25_file_path)
    else:
        logger.warning("BM25 index not found at %s — keyword search disabled", bm25_file_path)

    return vector_store, bm25_retriever


def clear_hybrid_store(vectorstore: PineconeVectorStore, persist_dir: str) -> None:
    """Clear all vectors from Pinecone and delete local BM25 directory."""
    logger.info("Clearing Knowledge Base: Vector database and BM25.")
    
    try:
        vectorstore.delete(delete_all=True)
        logger.info("Deleted all vectors from Pinecone.")
    except Exception as exception:
        logger.error("Failed to delete from Pinecone: %s", exception)

    if os.path.exists(persist_dir):
        shutil.rmtree(persist_dir)
        os.makedirs(persist_dir, exist_ok=True)
        logger.info("Cleared BM25 index directory: %s", persist_dir)
