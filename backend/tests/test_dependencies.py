import pytest
from unittest.mock import patch, MagicMock
from app.core import dependencies

@pytest.fixture(autouse=True)
def reset_globals():
    dependencies.clear_global_store()
    dependencies._embedding_model = None
    dependencies._reranker = None
    yield

@patch("app.core.dependencies.get_embedding_model")
def test_get_lazy_embedding_model(mock_get_embedding_model):
    mock_model = MagicMock()
    mock_get_embedding_model.return_value = mock_model
    
    # First call should load it
    model1 = dependencies.get_lazy_embedding_model()
    assert model1 == mock_model
    mock_get_embedding_model.assert_called_once()
    
    # Second call should return cached
    model2 = dependencies.get_lazy_embedding_model()
    assert model2 == mock_model
    assert mock_get_embedding_model.call_count == 1

@patch("app.core.dependencies.get_lazy_embedding_model")
@patch("app.core.dependencies.load_vector_store")
def test_get_lazy_vector_store(mock_load_vector_store, mock_get_lazy_embedding_model):
    mock_store = MagicMock()
    mock_load_vector_store.return_value = mock_store
    
    # First call should load it
    store1 = dependencies.get_lazy_vector_store()
    assert store1 == mock_store
    mock_load_vector_store.assert_called_once()
    mock_get_lazy_embedding_model.assert_called_once()
    
    # Second call should return cached
    store2 = dependencies.get_lazy_vector_store()
    assert store2 == mock_store
    assert mock_load_vector_store.call_count == 1

@patch("app.core.dependencies.get_reranker")
def test_get_lazy_reranker(mock_get_reranker):
    mock_reranker = MagicMock()
    mock_get_reranker.return_value = mock_reranker
    
    # First call should load it
    reranker1 = dependencies.get_lazy_reranker()
    assert reranker1 == mock_reranker
    mock_get_reranker.assert_called_once()
    
    # Second call should return cached
    reranker2 = dependencies.get_lazy_reranker()
    assert reranker2 == mock_reranker
    assert mock_get_reranker.call_count == 1

def test_clear_global_store():
    dependencies._vector_store = "something"
    dependencies.clear_global_store()
    assert dependencies._vector_store is None
