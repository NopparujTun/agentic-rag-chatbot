"""Document blob storage behind a small put/get/clear interface.

Two adapters satisfy the same seam: ``S3DocumentStore`` for prod (S3/MinIO) and
``InMemoryDocumentStore`` for tests. The S3 adapter resolves its client, bucket,
and bucket-existence lazily on first use, so import time stays free of env reads
and network calls (the router is imported before ``load_dotenv()`` runs).
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Dict

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


class DocumentStore(ABC):
    """A blob store keyed by filename."""

    @abstractmethod
    def put(self, name: str, data: bytes) -> str:
        """Store ``data`` under ``name`` and return a locator."""

    @abstractmethod
    def get(self, name: str, local_path: str) -> str:
        """Download ``name`` to ``local_path`` and return ``local_path``."""

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored blobs."""


class S3DocumentStore(DocumentStore):
    """S3/MinIO-backed store. Client and bucket are resolved lazily on first use."""

    def __init__(self) -> None:
        self._client = None
        self._bucket = ""
        self._endpoint = ""

    def _ensure(self):
        if self._client is None:
            self._endpoint = os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000")
            self._bucket = os.environ.get("S3_BUCKET_NAME", "documents")
            self._client = boto3.client(
                "s3",
                endpoint_url=self._endpoint,
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin"),
                region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
            )
            try:
                self._client.head_bucket(Bucket=self._bucket)
            except ClientError as exc:
                if exc.response["Error"]["Code"] == "404":
                    self._client.create_bucket(Bucket=self._bucket)
                else:
                    logger.error(f"S3 Error checking bucket: {exc}")
        return self._client

    def put(self, name: str, data: bytes) -> str:
        client = self._ensure()
        try:
            client.put_object(Bucket=self._bucket, Key=name, Body=data)
            return f"{self._endpoint}/{self._bucket}/{name}"
        except ClientError as exc:
            logger.error(f"Failed to upload to S3: {exc}")
            raise

    def get(self, name: str, local_path: str) -> str:
        client = self._ensure()
        try:
            client.download_file(Bucket=self._bucket, Key=name, Filename=local_path)
            return local_path
        except ClientError as exc:
            logger.error(f"Failed to download {name} from S3: {exc}")
            raise

    def clear(self) -> None:
        client = self._ensure()
        try:
            response = client.list_objects_v2(Bucket=self._bucket)
            if "Contents" in response:
                objects = [{"Key": obj["Key"]} for obj in response["Contents"]]
                client.delete_objects(Bucket=self._bucket, Delete={"Objects": objects})
        except ClientError as exc:
            logger.error(f"Failed to clear S3 bucket contents: {exc}")
            raise


class InMemoryDocumentStore(DocumentStore):
    """In-memory adapter for tests."""

    def __init__(self) -> None:
        self._blobs: Dict[str, bytes] = {}

    def put(self, name: str, data: bytes) -> str:
        self._blobs[name] = data
        return f"memory://{name}"

    def get(self, name: str, local_path: str) -> str:
        with open(local_path, "wb") as file_handle:
            file_handle.write(self._blobs[name])
        return local_path

    def clear(self) -> None:
        self._blobs.clear()


document_store: DocumentStore = S3DocumentStore()


def get_document_store() -> DocumentStore:
    return document_store
