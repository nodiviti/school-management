"""Object Storage Service"""
from abc import ABC, abstractmethod
from typing import Optional, BinaryIO
import boto3
from botocore.client import Config
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


class StorageService(ABC):
    """Abstract storage service interface"""
    
    @abstractmethod
    async def upload_file(self, file: BinaryIO, object_name: str, content_type: str = None) -> str:
        """Upload file and return URL"""
        pass
    
    @abstractmethod
    async def download_file(self, object_name: str) -> bytes:
        """Download file"""
        pass
    
    @abstractmethod
    async def delete_file(self, object_name: str) -> bool:
        """Delete file"""
        pass
    
    @abstractmethod
    async def get_file_url(self, object_name: str, expires_in: int = 3600) -> str:
        """Get presigned URL for file"""
        pass


class MinIOStorage(StorageService):
    """MinIO storage service (S3-compatible)"""
    
    def __init__(self):
        self.client = boto3.client(
            's3',
            endpoint_url=f"http{'s' if settings.MINIO_USE_SSL else ''}://{settings.MINIO_ENDPOINT}",
            aws_access_key_id=settings.MINIO_ACCESS_KEY,
            aws_secret_access_key=settings.MINIO_SECRET_KEY,
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        self.bucket = settings.MINIO_BUCKET_NAME
        self._ensure_bucket_exists()
    
    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist"""
        try:
            self.client.head_bucket(Bucket=self.bucket)
        except:
            try:
                self.client.create_bucket(Bucket=self.bucket)
                logger.info(f"Created MinIO bucket: {self.bucket}")
            except Exception as e:
                logger.error(f"Failed to create bucket: {e}")
    
    async def upload_file(self, file: BinaryIO, object_name: str, content_type: str = None) -> str:
        """Upload file to MinIO"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_fileobj(file, self.bucket, object_name, ExtraArgs=extra_args)
            return await self.get_file_url(object_name)
        except Exception as e:
            logger.error(f"MinIO upload failed: {e}")
            raise
    
    async def download_file(self, object_name: str) -> bytes:
        """Download file from MinIO"""
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=object_name)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"MinIO download failed: {e}")
            raise
    
    async def delete_file(self, object_name: str) -> bool:
        """Delete file from MinIO"""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=object_name)
            return True
        except Exception as e:
            logger.error(f"MinIO delete failed: {e}")
            return False
    
    async def get_file_url(self, object_name: str, expires_in: int = 3600) -> str:
        """Get presigned URL"""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return ""


class S3Storage(StorageService):
    """AWS S3 storage service"""
    
    def __init__(self):
        self.client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket = settings.AWS_S3_BUCKET
    
    async def upload_file(self, file: BinaryIO, object_name: str, content_type: str = None) -> str:
        """Upload file to S3"""
        try:
            extra_args = {}
            if content_type:
                extra_args['ContentType'] = content_type
            
            self.client.upload_fileobj(file, self.bucket, object_name, ExtraArgs=extra_args)
            return await self.get_file_url(object_name)
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")
            raise
    
    async def download_file(self, object_name: str) -> bytes:
        """Download file from S3"""
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=object_name)
            return response['Body'].read()
        except Exception as e:
            logger.error(f"S3 download failed: {e}")
            raise
    
    async def delete_file(self, object_name: str) -> bool:
        """Delete file from S3"""
        try:
            self.client.delete_object(Bucket=self.bucket, Key=object_name)
            return True
        except Exception as e:
            logger.error(f"S3 delete failed: {e}")
            return False
    
    async def get_file_url(self, object_name: str, expires_in: int = 3600) -> str:
        """Get presigned URL"""
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': object_name},
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            return ""


def get_storage_service() -> StorageService:
    """Factory function to get configured storage service"""
    if settings.STORAGE_PROVIDER == "minio":
        return MinIOStorage()
    elif settings.STORAGE_PROVIDER == "s3":
        return S3Storage()
    elif settings.STORAGE_PROVIDER == "gcs":
        # TODO: Implement GCS
        raise NotImplementedError("GCS storage not yet implemented")
    elif settings.STORAGE_PROVIDER == "azure":
        # TODO: Implement Azure Blob
        raise NotImplementedError("Azure Blob storage not yet implemented")
    else:
        raise ValueError(f"Unsupported storage provider: {settings.STORAGE_PROVIDER}")