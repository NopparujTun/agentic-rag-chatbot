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
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.pdf_processor import process_file
from app.storage.vector_store import save_vector_store

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
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> Tuple[PineconeVectorStore, int, float]:
    """Process files from paths and index them into Pinecone.

    Args:
        file_paths: A list of paths to the files to ingest.
        embedding_model: The Pinecone Embeddings model to use.
        index_name: The name of the Pinecone index.
        chunk_size: The character limit per text chunk.
        chunk_overlap: The overlap size between text chunks.

    Returns:
        A tuple containing the initialized vector store, total chunks indexed,
        and total time taken in seconds.

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

    vector_store = save_vector_store(
        chunks=chunked_documents,
        embedding_model=embedding_model,
        index_name=index_name,
    )

    ingestion_duration = time.time() - start_time
    return vector_store, len(chunked_documents), ingestion_duration


def run_ingestion_background(filenames: list) -> None:
    """Background task that downloads files from S3, runs ingestion, and reloads the store.

    Designed to be registered with FastAPI ``BackgroundTasks`` — replaces the
    previous Celery ``ingest_documents_task``.

    Args:
        filenames: List of filenames already uploaded to S3.
    """
    import shutil
    import tempfile

    from app.core.dependencies import resources
    from app.core.config import load_config
    from app.services.document_store import document_store

    logger.info("Background ingestion started for %d file(s).", len(filenames))
    app_config = load_config()
    temp_dir = tempfile.mkdtemp()

    try:
        local_paths = []
        for filename in filenames:
            local_path = os.path.join(temp_dir, filename)
            document_store.get(filename, local_path)
            local_paths.append(local_path)

        embedding_model = resources.embedding_model()

        _, total_chunks, duration = run_ingestion_pipeline(
            file_paths=local_paths,
            embedding_model=embedding_model,
            index_name=app_config["vector_db"]["index_name"],
            chunk_size=app_config["ingestion"]["chunk_size"],
            chunk_overlap=app_config["ingestion"]["chunk_overlap"],
        )

        # Force the next request to reload the updated store from Pinecone
        resources.reset()
        logger.info(
            "Background ingestion complete: %d chunks in %.2fs. Store reloaded.",
            total_chunks,
            duration,
        )
    except Exception as exc:
        logger.error("Background ingestion failed: %s", exc)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
