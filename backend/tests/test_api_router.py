import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io

from main import app
from app.core import dependencies

client = TestClient(app)

@pytest.fixture(autouse=True)
def mock_dependencies():
    with patch("app.api.router.get_lazy_vector_store") as mock_vs, \
         patch("app.api.router.get_lazy_reranker") as mock_reranker:
        mock_vs.return_value = MagicMock()
        mock_reranker.return_value = MagicMock()
        yield mock_vs, mock_reranker

@patch("app.api.router.process_chat")
def test_chat_endpoint_success(mock_process_chat):
    mock_process_chat.return_value = {"answer": "Test response", "sources": []}
    
    response = client.post("/api/chat", json={"query": "test query", "chat_history": ""})
    assert response.status_code == 200
    assert response.json() == {"answer": "Test response", "sources": []}

@patch("app.api.router.process_chat")
def test_chat_endpoint_value_error(mock_process_chat):
    mock_process_chat.side_effect = ValueError("Invalid input")
    
    response = client.post("/api/chat", json={"query": "test query", "chat_history": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid input"

@patch("app.api.router.process_chat")
def test_chat_endpoint_generic_error(mock_process_chat):
    mock_process_chat.side_effect = Exception("Server error")
    
    response = client.post("/api/chat", json={"query": "test query", "chat_history": ""})
    assert response.status_code == 500
    assert response.json()["detail"] == "Server error"

@patch("app.api.router.upload_file_to_s3")
@patch("app.api.router.run_ingestion_background")
def test_upload_document_success(mock_run_ingestion, mock_upload_s3):
    mock_upload_s3.return_value = "s3://test/file.pdf"
    
    file_content = b"fake pdf content"
    files = [
        ("files", ("test1.pdf", io.BytesIO(file_content), "application/pdf")),
        ("files", ("test2.txt", io.BytesIO(file_content), "text/plain")),
        ("files", ("test3.jpg", io.BytesIO(file_content), "image/jpeg")) # Should be ignored
    ]
    
    response = client.post("/api/upload", files=files)
    
    assert response.status_code == 200
    assert "test1.pdf" in response.json()["files_processed"]
    assert "test2.txt" in response.json()["files_processed"]
    assert "test3.jpg" not in response.json()["files_processed"]
    assert mock_upload_s3.call_count == 2
    mock_run_ingestion.assert_called_once()

def test_upload_document_no_valid_files():
    file_content = b"fake content"
    files = [
        ("files", ("test.jpg", io.BytesIO(file_content), "image/jpeg"))
    ]
    
    response = client.post("/api/upload", files=files)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "No valid files provided. Supported formats: PDF, DOCX, TXT."

@patch("app.api.router.clear_vector_store")
@patch("app.api.router.clear_global_store")
def test_clear_kb_success(mock_clear_global, mock_clear_vs):
    response = client.post("/api/clear")
    assert response.status_code == 200
    assert response.json()["message"] == "Knowledge Base cleared successfully."
    mock_clear_vs.assert_called_once()
    mock_clear_global.assert_called_once()

@patch("app.api.router.get_lazy_vector_store")
def test_clear_kb_error(mock_get_vs):
    mock_get_vs.side_effect = Exception("Clear error")
    
    response = client.post("/api/clear")
    assert response.status_code == 500
    assert response.json()["detail"] == "Clear error"

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
