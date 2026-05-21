import pytest
from unittest.mock import patch, MagicMock
from botocore.exceptions import ClientError
from app.services import s3_service

@patch("app.services.s3_service.boto3.client")
def test_get_s3_client(mock_boto_client):
    mock_boto_client.return_value = "mock_client"
    client = s3_service.get_s3_client()
    assert client == "mock_client"
    mock_boto_client.assert_called_once()

@patch("app.services.s3_service.get_s3_client")
def test_ensure_bucket_exists_exists(mock_get_client):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    s3_service.ensure_bucket_exists()
    mock_client.head_bucket.assert_called_once()

@patch("app.services.s3_service.get_s3_client")
def test_ensure_bucket_exists_not_exists(mock_get_client):
    mock_client = MagicMock()
    mock_client.head_bucket.side_effect = ClientError({"Error": {"Code": "404"}}, "head_bucket")
    mock_get_client.return_value = mock_client
    
    s3_service.ensure_bucket_exists()
    mock_client.head_bucket.assert_called_once()
    mock_client.create_bucket.assert_called_once()

@patch("app.services.s3_service.get_s3_client")
def test_ensure_bucket_exists_error(mock_get_client):
    mock_client = MagicMock()
    mock_client.head_bucket.side_effect = ClientError({"Error": {"Code": "500"}}, "head_bucket")
    mock_get_client.return_value = mock_client
    
    s3_service.ensure_bucket_exists()
    mock_client.head_bucket.assert_called_once()
    mock_client.create_bucket.assert_not_called()

@patch("app.services.s3_service.ensure_bucket_exists")
@patch("app.services.s3_service.get_s3_client")
def test_upload_file_to_s3(mock_get_client, mock_ensure_bucket):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    result = s3_service.upload_file_to_s3(b"content", "test.pdf")
    assert result.endswith("/test.pdf")
    mock_client.put_object.assert_called_once()

@patch("app.services.s3_service.ensure_bucket_exists")
@patch("app.services.s3_service.get_s3_client")
def test_upload_file_to_s3_error(mock_get_client, mock_ensure_bucket):
    mock_client = MagicMock()
    mock_client.put_object.side_effect = ClientError({"Error": {"Code": "500"}}, "put_object")
    mock_get_client.return_value = mock_client
    
    with pytest.raises(ClientError):
        s3_service.upload_file_to_s3(b"content", "test.pdf")

@patch("app.services.s3_service.ensure_bucket_exists")
@patch("app.services.s3_service.get_s3_client")
def test_download_file_from_s3(mock_get_client, mock_ensure_bucket):
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    
    result = s3_service.download_file_from_s3("test.pdf", "/local/test.pdf")
    assert result == "/local/test.pdf"
    mock_client.download_file.assert_called_once()

@patch("app.services.s3_service.ensure_bucket_exists")
@patch("app.services.s3_service.get_s3_client")
def test_download_file_from_s3_error(mock_get_client, mock_ensure_bucket):
    mock_client = MagicMock()
    mock_client.download_file.side_effect = ClientError({"Error": {"Code": "500"}}, "download_file")
    mock_get_client.return_value = mock_client
    
    with pytest.raises(ClientError):
        s3_service.download_file_from_s3("test.pdf", "/local/test.pdf")

@patch("app.services.s3_service.ensure_bucket_exists")
@patch("app.services.s3_service.get_s3_client")
def test_delete_s3_bucket_contents(mock_get_client, mock_ensure_bucket):
    mock_client = MagicMock()
    mock_client.list_objects_v2.return_value = {"Contents": [{"Key": "test.pdf"}]}
    mock_get_client.return_value = mock_client
    
    s3_service.delete_s3_bucket_contents()
    mock_client.delete_objects.assert_called_once_with(
        Bucket="documents",
        Delete={'Objects': [{'Key': 'test.pdf'}]}
    )

@patch("app.services.s3_service.ensure_bucket_exists")
@patch("app.services.s3_service.get_s3_client")
def test_delete_s3_bucket_contents_empty(mock_get_client, mock_ensure_bucket):
    mock_client = MagicMock()
    mock_client.list_objects_v2.return_value = {}
    mock_get_client.return_value = mock_client
    
    s3_service.delete_s3_bucket_contents()
    mock_client.delete_objects.assert_not_called()
