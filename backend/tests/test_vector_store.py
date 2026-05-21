import pytest
from unittest.mock import patch, MagicMock
from langchain_core.documents import Document

from app.storage import vector_store

@patch("app.storage.vector_store.PineconeVectorStore")
def test_save_vector_store(mock_pinecone):
    mock_pinecone.from_documents.return_value = "mock_store"
    
    docs = [Document(page_content="test")]
    embedding_model = MagicMock()
    
    result = vector_store.save_vector_store(docs, embedding_model, "test_index")
    
    assert result == "mock_store"
    mock_pinecone.from_documents.assert_called_once_with(
        documents=docs,
        embedding=embedding_model,
        index_name="test_index"
    )

@patch("app.storage.vector_store.PineconeVectorStore")
def test_load_vector_store(mock_pinecone):
    mock_pinecone.return_value = "mock_store"
    
    embedding_model = MagicMock()
    
    result = vector_store.load_vector_store(embedding_model, "test_index")
    
    assert result == "mock_store"
    mock_pinecone.assert_called_once_with(
        index_name="test_index",
        embedding=embedding_model
    )

def test_clear_vector_store_success():
    mock_store = MagicMock()
    vector_store.clear_vector_store(mock_store)
    mock_store.delete.assert_called_once_with(delete_all=True)

def test_clear_vector_store_error():
    mock_store = MagicMock()
    mock_store.delete.side_effect = Exception("Delete error")
    vector_store.clear_vector_store(mock_store)
    mock_store.delete.assert_called_once_with(delete_all=True)
