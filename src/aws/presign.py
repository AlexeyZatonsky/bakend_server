from uuid import UUID

from typing import Any, Dict
from types_aiobotocore_s3.client import S3Client

from .client import get_s3_client
from .key_strategies import ObjectKind
from .dependencies import _ensure_bucket, build_object_key

from ..settings.config import settings

_SIGN_EXPIRES_DEFAULT = 60 * 60 


async def generate_presigned_upload_urls(
    *,
    owner_id: UUID,
    object_kind: ObjectKind,
    content_type: str,
    expires_in_second: int = _SIGN_EXPIRES_DEFAULT,
    **context: Any
) -> Dict[str, str]:
    """Генерирует presigned PUT‑URL и public‑URL для аватара пользователя."""
    client: S3Client = await get_s3_client()  # type: ignore[assignment]
    bucket = str(owner_id).lower()
    await _ensure_bucket(client, bucket)

    object_key = build_object_key(object_kind, **context)

    upload_url = await client.generate_presigned_url(
        "put_object",
        Params={
            "Bucket": bucket,
            "Key": object_key,
            "ContentType": content_type,
        },
        ExpiresIn=expires_in_second,
    )

    public_url = f"{settings.S3_URL}/{bucket}/{object_key}"
    return {
        "upload_url": upload_url,
        "public_url": public_url,
        "bucket": bucket,
        "key": object_key,
    }