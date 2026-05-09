"""S3/MinIO Integration service."""

import os
import logging
import boto3
from botocore.exceptions import ClientError
from typing import Optional

logger = logging.getLogger(__name__)

def get_s3_client():
    return boto3.client(
        's3',
        endpoint_url=os.environ.get("S3_ENDPOINT_URL", "http://localhost:9000"),
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin"),
        region_name=os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    )

def ensure_bucket_exists():
    s3 = get_s3_client()
    bucket_name = os.environ.get("S3_BUCKET_NAME", "documents")
    try:
        s3.head_bucket(Bucket=bucket_name)
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            s3.create_bucket(Bucket=bucket_name)
        else:
            logger.error(f"S3 Error checking bucket: {e}")

def upload_file_to_s3(file_bytes: bytes, filename: str) -> str:
    ensure_bucket_exists()
    s3 = get_s3_client()
    bucket_name = os.environ.get("S3_BUCKET_NAME", "documents")
    
    try:
        s3.put_object(Bucket=bucket_name, Key=filename, Body=file_bytes)
        return f"{os.environ.get('S3_ENDPOINT_URL', 'http://localhost:9000')}/{bucket_name}/{filename}"
    except ClientError as e:
        logger.error(f"Failed to upload to S3: {e}")
        raise e

def download_file_from_s3(filename: str, local_path: str) -> str:
    ensure_bucket_exists()
    s3 = get_s3_client()
    bucket_name = os.environ.get("S3_BUCKET_NAME", "documents")
    
    try:
        s3.download_file(Bucket=bucket_name, Key=filename, Filename=local_path)
        return local_path
    except ClientError as e:
        logger.error(f"Failed to download {filename} from S3: {e}")
        raise e

def delete_s3_bucket_contents():
    ensure_bucket_exists()
    s3 = get_s3_client()
    bucket_name = os.environ.get("S3_BUCKET_NAME", "documents")
    
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in response:
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            s3.delete_objects(Bucket=bucket_name, Delete={'Objects': objects_to_delete})
    except ClientError as e:
        logger.error(f"Failed to delete S3 bucket contents: {e}")
        raise e
