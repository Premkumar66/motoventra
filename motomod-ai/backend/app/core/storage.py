"""
MotoMod AI — MinIO (S3-compatible) Storage Client
Async file upload, download, presigned URLs, and bucket management
"""
import io
import mimetypes
from pathlib import Path
from typing import BinaryIO, Optional
from uuid import uuid4

from minio import Minio
from minio.error import S3Error
from minio.commonconfig import Tags

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


class StorageClient:
    """MinIO storage client with full lifecycle management."""

    def __init__(self):
        self._client: Optional[Minio] = None
        self._initialized = False

    def _get_client(self) -> Minio:
        if self._client is None:
            self._client = Minio(
                endpoint=settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE,
            )
        return self._client

    async def initialize_buckets(self) -> None:
        """Create all required buckets if they don't exist."""
        import socket
        try:
            parts = settings.MINIO_ENDPOINT.split(":")
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 9000
            # Rapid raw TCP port check with 0.5s timeout
            with socket.create_connection((host, port), timeout=0.5):
                pass
        except Exception as e:
            logger.warning("storage_offline_skipping_bucket_initialization", endpoint=settings.MINIO_ENDPOINT, error=str(e))
            return

        client = self._get_client()
        buckets = [
            settings.MINIO_BUCKET_BIKES,
            settings.MINIO_BUCKET_MODS,
            settings.MINIO_BUCKET_USERS,
            settings.MINIO_BUCKET_BUILDS,
            settings.MINIO_BUCKET_ML,
            settings.MINIO_BUCKET_DATASETS,
        ]
        for bucket in buckets:
            try:
                if not client.bucket_exists(bucket):
                    client.make_bucket(bucket)
                    logger.info("bucket_created", bucket=bucket)
                else:
                    logger.debug("bucket_exists", bucket=bucket)
            except S3Error as e:
                logger.error("bucket_creation_failed", bucket=bucket, error=str(e))
                raise

        self._initialized = True
        logger.info("storage_initialized", buckets=buckets)

    def upload_file(
        self,
        bucket: str,
        object_name: str,
        data: BinaryIO,
        length: int,
        content_type: str = "application/octet-stream",
        tags: Optional[dict] = None,
    ) -> str:
        """
        Upload a file to MinIO.

        Returns:
            Full object URL (internal)
        """
        client = self._get_client()
        try:
            minio_tags = Tags.new_object_tags()
            if tags:
                for k, v in tags.items():
                    minio_tags[k] = str(v)

            client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=data,
                length=length,
                content_type=content_type,
                tags=minio_tags if tags else None,
            )
            url = f"/{bucket}/{object_name}"
            logger.info("file_uploaded", bucket=bucket, object=object_name, size=length)
            return url
        except S3Error as e:
            logger.error("file_upload_failed", bucket=bucket, object=object_name, error=str(e))
            raise

    def upload_bytes(
        self,
        bucket: str,
        object_name: str,
        content: bytes,
        content_type: str = "application/octet-stream",
        tags: Optional[dict] = None,
    ) -> str:
        """Upload bytes directly."""
        return self.upload_file(
            bucket=bucket,
            object_name=object_name,
            data=io.BytesIO(content),
            length=len(content),
            content_type=content_type,
            tags=tags,
        )

    def get_presigned_url(
        self,
        bucket: str,
        object_name: str,
        expires_seconds: int = 3600,
    ) -> str:
        """Generate a presigned URL for client-side download."""
        from datetime import timedelta
        client = self._get_client()
        try:
            url = client.presigned_get_object(
                bucket_name=bucket,
                object_name=object_name,
                expires=timedelta(seconds=expires_seconds),
            )
            return url
        except S3Error as e:
            logger.error("presigned_url_failed", bucket=bucket, object=object_name, error=str(e))
            raise

    def get_presigned_upload_url(
        self,
        bucket: str,
        object_name: str,
        expires_seconds: int = 3600,
    ) -> str:
        """Generate a presigned URL for direct client-side upload."""
        from datetime import timedelta
        client = self._get_client()
        try:
            url = client.presigned_put_object(
                bucket_name=bucket,
                object_name=object_name,
                expires=timedelta(seconds=expires_seconds),
            )
            return url
        except S3Error as e:
            logger.error("presigned_upload_url_failed", bucket=bucket, object=object_name, error=str(e))
            raise

    def delete_file(self, bucket: str, object_name: str) -> bool:
        """Delete an object from MinIO."""
        client = self._get_client()
        try:
            client.remove_object(bucket, object_name)
            logger.info("file_deleted", bucket=bucket, object=object_name)
            return True
        except S3Error as e:
            logger.error("file_delete_failed", bucket=bucket, object=object_name, error=str(e))
            return False

    def file_exists(self, bucket: str, object_name: str) -> bool:
        """Check if an object exists."""
        client = self._get_client()
        try:
            client.stat_object(bucket, object_name)
            return True
        except S3Error:
            return False

    def generate_object_name(self, original_filename: str, prefix: str = "") -> str:
        """Generate a unique object name to prevent collisions."""
        ext = Path(original_filename).suffix.lower()
        unique_id = uuid4().hex
        if prefix:
            return f"{prefix}/{unique_id}{ext}"
        return f"{unique_id}{ext}"

    def get_public_url(self, bucket: str, object_name: str) -> str:
        """Get the internal public URL for an object."""
        protocol = "https" if settings.MINIO_SECURE else "http"
        return f"{protocol}://{settings.MINIO_ENDPOINT}/{bucket}/{object_name}"

    async def check_connection(self) -> bool:
        """Health check for MinIO connectivity."""
        import socket
        try:
            parts = settings.MINIO_ENDPOINT.split(":")
            host = parts[0]
            port = int(parts[1]) if len(parts) > 1 else 9000
            with socket.create_connection((host, port), timeout=0.5):
                pass
        except Exception:
            return False

        try:
            client = self._get_client()
            client.list_buckets()
            return True
        except Exception as e:
            logger.error("minio_health_check_failed", error=str(e))
            return False


# Global storage client instance
storage_client = StorageClient()


# FastAPI dependency
async def get_storage() -> StorageClient:
    return storage_client
