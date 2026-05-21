import pytest
from unittest.mock import patch, MagicMock
from app.services import ingestion_service
from langchain_core.documents import Document

def test_clean_pdf_text():
    raw = "Test   string ํา with Aก กA and  :  spacing\n\n\n\nnewlines"
    cleaned = ingestion_service.clean_pdf_text(raw)
    assert cleaned == "Test string ำ with A ก ก A and:spacing\n\nnewlines"

def test_chunk_documents():
    docs = [Document(page_content="A " * 500)]
    chunked = ingestion_service.chunk_documents(docs, chunk_size=100, chunk_overlap=20)
    assert len(chunked) > 1

@patch("app.services.ingestion_service.process_uploaded_file_path")
def test_process_uploaded_file(mock_process_path):
    mock_process_path.return_value = [Document(page_content="test")]
    result = ingestion_service.process_uploaded_file(b"test")
    assert len(result) == 1
    assert result[0].page_content == "test"

@patch("app.services.ingestion_service.process_file")
@patch("builtins.open")
def test_process_uploaded_file_path(mock_open, mock_process_file):
    mock_process_file.return_value = "test.md"
    mock_open.return_value.__enter__.return_value.read.return_value = "markdown content"
    
    result = ingestion_service.process_uploaded_file_path("test.pdf")
    
    assert len(result) == 1
    assert result[0].page_content == "markdown content"
    assert result[0].metadata["source"] == "test.pdf"

@patch("app.services.ingestion_service.process_file")
def test_process_uploaded_file_path_error(mock_process_file):
    mock_process_file.side_effect = Exception("error")
    result = ingestion_service.process_uploaded_file_path("test.pdf")
    assert result == []

@patch("app.services.ingestion_service.process_uploaded_file_path")
@patch("app.services.ingestion_service.chunk_documents")
@patch("app.services.ingestion_service.save_vector_store")
def test_run_ingestion_pipeline(mock_save, mock_chunk, mock_process):
    mock_process.return_value = [Document(page_content="test")]
    mock_chunk.return_value = [Document(page_content="chunk1")]
    mock_save.return_value = "mock_store"
    
    store, total, duration = ingestion_service.run_ingestion_pipeline(
        ["test.pdf"], "model", "index", 100, 20
    )
    
    assert store == "mock_store"
    assert total == 1
    assert duration > 0

@patch("app.services.ingestion_service.process_uploaded_file_path")
@patch("app.services.ingestion_service.chunk_documents")
def test_run_ingestion_pipeline_empty(mock_chunk, mock_process):
    mock_process.return_value = [Document(page_content="test")]
    mock_chunk.return_value = []
    
    with pytest.raises(ValueError):
        ingestion_service.run_ingestion_pipeline(["test.pdf"], "model", "index")

@patch("app.services.s3_service.download_file_from_s3")
@patch("app.core.dependencies.get_lazy_embedding_model")
@patch("app.services.ingestion_service.run_ingestion_pipeline")
@patch("app.core.dependencies.clear_global_store")
@patch("app.core.config.load_config")
def test_run_ingestion_background(mock_load_config, mock_clear, mock_run, mock_get_model, mock_download):
    mock_load_config.return_value = {
        "vector_db": {"index_name": "test"},
        "ingestion": {"chunk_size": 100, "chunk_overlap": 20}
    }
    mock_get_model.return_value = "model"
    mock_run.return_value = ("store", 1, 1.0)
    
    ingestion_service.run_ingestion_background(["test.pdf"])
    
    mock_download.assert_called_once()
    mock_run.assert_called_once()
    mock_clear.assert_called_once()
