"""Ingestion pipeline module to orchestrate document loading, chunking, and indexing.

This module provides functions to process uploaded files, split text into chunks,
and store the resulting embeddings in a vector store.
"""

import logging
import os
import re
import tempfile
import time
from typing import List, Tuple

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_community.retrievers import BM25Retriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.ingestion.pdf_processor import process_file
from src.rag.retrieval import save_hybrid_store

logger = logging.getLogger(__name__)


def clean_pdf_text(raw_text: str) -> str:
    """Normalize mixed Thai and English text extracted from a file.

    Processing steps:
    1. Fix Thai broken vowel.
    2. Insert space between English and Thai character boundaries.
    3. Normalize colons.
    4. Clean up spaces but preserve newlines.

    Args:
        raw_text: The extracted raw text string.

    Returns:
        The normalized text string.
    """
    normalized_text = raw_text.replace("ํา", "ำ")
    normalized_text = re.sub(r"([a-zA-Z])([ก-๙])", r"\1 \2", normalized_text)
    normalized_text = re.sub(r"([ก-๙])([a-zA-Z])", r"\1 \2", normalized_text)
    normalized_text = re.sub(r"\s*:\s*", ":", normalized_text)
    normalized_text = re.sub(r"[ \t]+", " ", normalized_text)
    normalized_text = re.sub(r"\n{3,}", "\n\n", normalized_text)
    return normalized_text.strip()


def chunk_documents(
    documents: List[Document],
    chunk_size: int,
    chunk_overlap: int,
) -> List[Document]:
    """Split documents into smaller, overlapping chunks for embedding.

    Args:
        documents: A list of LangChain Document objects to split.
        chunk_size: Maximum character count per chunk.
        chunk_overlap: Number of overlapping characters between chunks.

    Returns:
        A list of chunked Document objects.
    """
    for document in documents:
        document.page_content = clean_pdf_text(document.page_content)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "  ", " ", ""],
        length_function=len,
    )

    chunked_documents = text_splitter.split_documents(documents)
    logger.info(
        "Chunked %d documents -> %d chunks (size=%d chars, overlap=%d chars)",
        len(documents), len(chunked_documents), chunk_size, chunk_overlap,
    )
    return chunked_documents


def process_uploaded_file(file_bytes: bytes) -> List[Document]:
    """Parse file bytes by writing to a temporary file, then loading.

    Args:
        file_bytes: The raw bytes of the uploaded file.

    Returns:
        A list of extracted LangChain Document objects.
    """
    temporary_path = ""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(file_bytes)
            temporary_path = temp_file.name
        return process_uploaded_file_path(temporary_path)
    finally:
        if temporary_path and os.path.exists(temporary_path):
            os.unlink(temporary_path)


def process_uploaded_file_path(file_path: str) -> List[Document]:
    """Parse a file from a specified file path.

    Args:
        file_path: The absolute or relative path to the file.

    Returns:
        A list containing the extracted document as a LangChain Document.
    """
    logger.info("Loading file via Docling Pipeline: %s", file_path)
    output_directory = os.path.join(os.path.dirname(file_path), "md_output")
    os.makedirs(output_directory, exist_ok=True)

    try:
        markdown_file_path = process_file(file_path=file_path, output_dir=output_directory)
        with open(markdown_file_path, "r", encoding="utf-8") as file_handle:
            markdown_content = file_handle.read()
        return [Document(
            page_content=markdown_content,
            metadata={"source": file_path}
        )]
    except Exception as exception:
        logger.error(f"Failed to process {file_path}: {exception}")
        return []


def run_ingestion_pipeline(
    file_paths: List[str],
    embedding_model: Embeddings,
    index_name: str,
    persist_dir: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> Tuple[PineconeVectorStore, BM25Retriever, int, float]:
    """Process files from paths and index them into the hybrid store.

    Args:
        file_paths: A list of paths to the files to ingest.
        embedding_model: The Pinecone Embeddings model to use.
        index_name: The name of the Pinecone index.
        persist_dir: The directory to persist local data like BM25.
        chunk_size: The character limit per text chunk.
        chunk_overlap: The overlap size between text chunks.

    Returns:
        A tuple containing the initialized VectorStore, BM25Retriever, 
        total chunks indexed, and total time taken in seconds.

    Raises:
        ValueError: If no text was successfully extracted and chunked.
    """
    start_time = time.time()

    all_documents = []
    for path in file_paths:
        all_documents.extend(process_uploaded_file_path(path))

    chunked_documents = chunk_documents(all_documents, chunk_size, chunk_overlap)
    if not chunked_documents:
        raise ValueError("No text found in the provided documents.")

    vector_store, bm25_retriever = save_hybrid_store(
        chunks=chunked_documents,
        embedding_model=embedding_model,
        persist_dir=persist_dir,
        index_name=index_name,
    )

    ingestion_duration = time.time() - start_time
    return vector_store, bm25_retriever, len(chunked_documents), ingestion_duration
