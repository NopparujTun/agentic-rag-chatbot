from unittest.mock import patch, MagicMock
from app.core import dependencies
from app.core.dependencies import Resources


@patch("app.core.dependencies.PineconeEmbeddings")
def test_embedding_model_lazy_and_cached(mock_embeddings):
    mock_embeddings.return_value = MagicMock()
    res = Resources()

    model1 = res.embedding_model()
    model2 = res.embedding_model()

    assert model1 is model2
    mock_embeddings.assert_called_once()


@patch("app.core.dependencies.load_vector_store")
@patch("app.core.dependencies.PineconeEmbeddings")
def test_vector_store_lazy_and_cached(mock_embeddings, mock_load_vector_store):
    mock_load_vector_store.return_value = MagicMock()
    res = Resources()

    store1 = res.vector_store()
    store2 = res.vector_store()

    assert store1 is store2
    mock_load_vector_store.assert_called_once()
    mock_embeddings.assert_called_once()


@patch("app.core.dependencies.CrossEncoder")
def test_reranker_lazy_and_cached(mock_cross_encoder):
    mock_cross_encoder.return_value = MagicMock()
    res = Resources()

    reranker1 = res.reranker()
    reranker2 = res.reranker()

    assert reranker1 is reranker2
    mock_cross_encoder.assert_called_once()


@patch("app.core.dependencies.load_vector_store")
@patch("app.core.dependencies.PineconeEmbeddings")
def test_reset_forces_vector_store_reload(mock_embeddings, mock_load_vector_store):
    mock_load_vector_store.return_value = MagicMock()
    res = Resources()

    res.vector_store()
    res.reset()
    res.vector_store()

    assert mock_load_vector_store.call_count == 2


@patch("app.core.dependencies.clear_vector_store")
@patch("app.core.dependencies.load_vector_store")
@patch("app.core.dependencies.PineconeEmbeddings")
def test_clear_knowledge_base_wipes_and_resets(mock_embeddings, mock_load_vector_store, mock_clear):
    store = MagicMock()
    mock_load_vector_store.return_value = store
    res = Resources()

    res.clear_knowledge_base()

    mock_clear.assert_called_once_with(store)
    assert res._vector_store is None


def test_status_does_not_force_a_load():
    res = Resources()
    assert res.status() == {"models_loaded": False, "kb_ready": False}


def test_get_resources_returns_singleton():
    assert dependencies.get_resources() is dependencies.resources
