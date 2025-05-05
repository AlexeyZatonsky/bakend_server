import asyncio
from typing import Any, Optional

from aiobotocore.session import get_session
from botocore.config import Config

from types_aiobotocore_s3.client import S3Client

from ..settings.config import settings


_REGION = "us-east-1"  # для MinIO регион произвольный, но задаём по умолчанию


class _S3ClientFactory:

    _session = get_session()

    def __init__(self):
        self._client: Optional[Any] = None
        self._lock = asyncio.Lock()


    async def get_client(self) -> S3Client:
        async with self._lock:
            if self._client is None:
                self._client = await self._session.create_client(
                    "s3",
                    endpoint_url = settings.S3_URL,
                    region_name = _REGION,
                    aws_access_key_id=settings.S3_ACCESS_KEY,
                    aws_secret_access_key=settings.S3_SECRET_KEY,
                    config=Config(signature_version="s3v4"),
                ).__aenter__()
            return self._client
        
    async def close(self) -> None:
        async with self._lock:
            if self._client is not None:
                await self._client.__aexit__(None, None, None)
                self._client = None


_factory = _S3ClientFactory()

async def get_s3_client():
    return await _factory.get_client()

async def close_s3_client() -> None:
    await _factory.close()

