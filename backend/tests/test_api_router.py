import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import io

from main import app
from app.core.dependencies import get_resources
from app.services.document_store import get_document_store, InMemoryDocumentStore

client = TestClient(app)


class FakeResources:
    """A stand-in adapter for the Resources seam, swapped in via dependency_overrides."""

    def __init__(self):
        self._vector_store = MagicMock()
        self._reranker = MagicMock()
        self.cleared = False

    def vector_store(self):
        return self._vector_store

    def reranker(self):
        return self._reranker

    def clear_knowledge_base(self):
        self.cleared = True

    def status(self):
        return {"models_loaded": True, "kb_ready": True}


@pytest.fixture
def fake_resources():
    res = FakeResources()
    app.dependency_overrides[get_resources] = lambda: res
    yield res
    app.dependency_overrides.pop(get_resources, None)


@pytest.fixture
def in_memory_store():
    store = InMemoryDocumentStore()
    app.dependency_overrides[get_document_store] = lambda: store
    yield store
    app.dependency_overrides.pop(get_document_store, None)


@patch("app.api.router.answer_query")
def test_chat_endpoint_success(mock_answer_query, fake_resources):
    mock_answer_query.return_value = {"answer": "Test response", "sources": []}

    response = client.post("/api/chat", json={"query": "test query", "chat_history": ""})
    assert response.status_code == 200
    assert response.json() == {"answer": "Test response", "sources": []}


@patch("app.api.router.answer_query")
def test_chat_endpoint_value_error(mock_answer_query, fake_resources):
    mock_answer_query.side_effect = ValueError("Invalid input")

    response = client.post("/api/chat", json={"query": "test query", "chat_history": ""})
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid input"


@patch("app.api.router.answer_query")
def test_chat_endpoint_generic_error(mock_answer_query, fake_resources):
    mock_answer_query.side_effect = Exception("Server error")

    response = client.post("/api/chat", json={"query": "test query", "chat_history": ""})
    assert response.status_code == 500
    assert response.json()["detail"] == "Server error"


@patch("app.api.router.run_ingestion_background")
def test_upload_document_success(mock_run_ingestion, in_memory_store):
    file_content = b"fake pdf content"
    files = [
        ("files", ("test1.pdf", io.BytesIO(file_content), "application/pdf")),
        ("files", ("test2.txt", io.BytesIO(file_content), "text/plain")),
        ("files", ("test3.jpg", io.BytesIO(file_content), "image/jpeg")),  # ignored
    ]

    response = client.post("/api/upload", files=files)

    assert response.status_code == 200
    body = response.json()
    assert "test1.pdf" in body["files_processed"]
    assert "test2.txt" in body["files_processed"]
    assert "test3.jpg" not in body["files_processed"]
    assert set(in_memory_store._blobs) == {"test1.pdf", "test2.txt"}
    mock_run_ingestion.assert_called_once()


def test_upload_document_no_valid_files(in_memory_store):
    files = [("files", ("test.jpg", io.BytesIO(b"fake content"), "image/jpeg"))]

    response = client.post("/api/upload", files=files)

    assert response.status_code == 400
    assert response.json()["detail"] == "No valid files provided. Supported formats: PDF, DOCX, TXT."


def test_clear_kb_success(fake_resources):
    response = client.post("/api/clear")
    assert response.status_code == 200
    assert response.json()["message"] == "Knowledge Base cleared successfully."
    assert fake_resources.cleared is True


def test_clear_kb_error():
    res = MagicMock()
    res.clear_knowledge_base.side_effect = Exception("Clear error")
    app.dependency_overrides[get_resources] = lambda: res
    try:
        response = client.post("/api/clear")
        assert response.status_code == 500
        assert response.json()["detail"] == "Clear error"
    finally:
        app.dependency_overrides.pop(get_resources, None)


def test_health_check(fake_resources):
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["models_loaded"] is True
    assert body["kb_ready"] is True
