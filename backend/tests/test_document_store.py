import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from app.services.document_store import (
    S3DocumentStore,
    InMemoryDocumentStore,
    get_document_store,
    document_store,
)


# --- InMemoryDocumentStore: the test adapter, no patching needed ---

def test_inmemory_put_get_roundtrip(tmp_path):
    store = InMemoryDocumentStore()
    locator = store.put("a.pdf", b"hello")
    assert locator == "memory://a.pdf"

    local = tmp_path / "a.pdf"
    assert store.get("a.pdf", str(local)) == str(local)
    assert local.read_bytes() == b"hello"


def test_inmemory_clear():
    store = InMemoryDocumentStore()
    store.put("a.pdf", b"x")
    store.clear()
    with pytest.raises(KeyError):
        store.get("a.pdf", "/tmp/whatever")


# --- S3DocumentStore: patch boto3 once at the seam ---

@patch("app.services.document_store.boto3.client")
def test_s3_put(mock_client_factory):
    client = MagicMock()
    mock_client_factory.return_value = client

    result = S3DocumentStore().put("test.pdf", b"content")

    assert result.endswith("/test.pdf")
    client.put_object.assert_called_once()


@patch("app.services.document_store.boto3.client")
def test_s3_put_error(mock_client_factory):
    client = MagicMock()
    client.put_object.side_effect = ClientError({"Error": {"Code": "500"}}, "put_object")
    mock_client_factory.return_value = client

    with pytest.raises(ClientError):
        S3DocumentStore().put("test.pdf", b"content")


@patch("app.services.document_store.boto3.client")
def test_s3_get(mock_client_factory):
    client = MagicMock()
    mock_client_factory.return_value = client

    result = S3DocumentStore().get("test.pdf", "/local/test.pdf")

    assert result == "/local/test.pdf"
    client.download_file.assert_called_once()


@patch("app.services.document_store.boto3.client")
def test_s3_get_error(mock_client_factory):
    client = MagicMock()
    client.download_file.side_effect = ClientError({"Error": {"Code": "500"}}, "download_file")
    mock_client_factory.return_value = client

    with pytest.raises(ClientError):
        S3DocumentStore().get("test.pdf", "/local/test.pdf")


@patch("app.services.document_store.boto3.client")
def test_s3_creates_bucket_when_missing(mock_client_factory):
    client = MagicMock()
    client.head_bucket.side_effect = ClientError({"Error": {"Code": "404"}}, "head_bucket")
    mock_client_factory.return_value = client

    S3DocumentStore().put("test.pdf", b"x")

    client.create_bucket.assert_called_once()


@patch("app.services.document_store.boto3.client")
def test_s3_ensures_bucket_once_across_calls(mock_client_factory):
    client = MagicMock()
    mock_client_factory.return_value = client

    store = S3DocumentStore()
    store.put("a.pdf", b"x")
    store.put("b.pdf", b"y")

    # client built once, bucket checked once — not per call
    mock_client_factory.assert_called_once()
    client.head_bucket.assert_called_once()


@patch("app.services.document_store.boto3.client")
def test_s3_clear(mock_client_factory):
    client = MagicMock()
    client.list_objects_v2.return_value = {"Contents": [{"Key": "a.pdf"}]}
    mock_client_factory.return_value = client

    S3DocumentStore().clear()

    client.delete_objects.assert_called_once_with(
        Bucket="documents",
        Delete={"Objects": [{"Key": "a.pdf"}]},
    )


@patch("app.services.document_store.boto3.client")
def test_s3_clear_empty(mock_client_factory):
    client = MagicMock()
    client.list_objects_v2.return_value = {}
    mock_client_factory.return_value = client

    S3DocumentStore().clear()

    client.delete_objects.assert_not_called()


def test_get_document_store_returns_singleton():
    assert get_document_store() is document_store
