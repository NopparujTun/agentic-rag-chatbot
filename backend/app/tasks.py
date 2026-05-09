import logging
import os
import shutil
import tempfile

from app.core.celery_app import celery_app
from app.services.ingestion_service import run_ingestion_pipeline
from app.services.s3_service import download_file_from_s3
from app.core.dependencies import get_lazy_embedding_model
from app.core.config import load_config
from app.storage.vector_store import load_hybrid_store

logger = logging.getLogger(__name__)
app_config = load_config()

@celery_app.task(name="app.tasks.ingest_documents")
def ingest_documents_task(filenames: list[str]) -> dict:
    """Celery task to ingest documents asynchronously.
    
    Args:
        filenames: List of filenames stored in S3.
        
    Returns:
        dict: A summary of the ingestion process.
    """
    logger.info(f"Starting ingestion task for {len(filenames)} files.")
    temp_dir = tempfile.mkdtemp()
    local_file_paths = []
    
    try:
        # Download files from S3
        for filename in filenames:
            local_path = os.path.join(temp_dir, filename)
            download_file_from_s3(filename, local_path)
            local_file_paths.append(local_path)

        embedding_model = get_lazy_embedding_model()
        
        # We need to make sure the vector store and bm25 retriever are initialized
        # properly in the worker before we add to them or we might get errors
        load_hybrid_store(
            embedding_model=embedding_model,
            persist_dir=app_config["vector_db"]["persist_directory"],
            index_name=app_config["vector_db"]["index_name"],
        )
        
        vector_store, bm25_retriever, total_indexed_chunks, ingestion_time = run_ingestion_pipeline(
            file_paths=local_file_paths,
            embedding_model=embedding_model,
            index_name=app_config["vector_db"]["index_name"],
            persist_dir=app_config["vector_db"]["persist_directory"],
            chunk_size=app_config["ingestion"]["chunk_size"],
            chunk_overlap=app_config["ingestion"]["chunk_overlap"]
        )
        
        logger.info(f"Ingestion successful: {total_indexed_chunks} chunks in {ingestion_time}s.")
        
        return {
            "status": "completed",
            "total_chunks": total_indexed_chunks,
            "ingestion_time_seconds": round(ingestion_time, 2),
            "files_processed": filenames
        }
    except Exception as e:
        logger.error(f"Ingestion task failed: {e}")
        raise e
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
