from uuid import UUID

from typing import Any, Dict
from types_aiobotocore_s3.client import S3Client
from botocore.exceptions import ClientError

from ..core.Enums.MIMETypeEnums import MimeEnum
from .client import get_s3_client
from .strategies import ObjectKind, build_key
from .access_policies import AccessPolicy

from ..settings.config import S3_ENV




import logging
from ..core.log import configure_logging

logger = logging.getLogger(__name__)



class StorageService:

    async def _ensure_bucket(self, client: S3Client, bucket_name: str) -> None:    
        try:
            await client.create_bucket(Bucket=bucket_name)
        except (
            client.exceptions.BucketAlreadyOwnedByYou,  
            client.exceptions.BucketAlreadyExists,      
        ):
            logger.debug(f"Бакет с именем {bucket_name} уже создан")
        except ClientError:
            logger.error(f"Другая ошибка клиента для создания бакета")
            raise

    async def generate_upload_urls(
        self,
        *,
        owner_id: UUID,
        object_kind: ObjectKind,
        content_type: MimeEnum,
        access: AccessPolicy = AccessPolicy.PUBLIC_READ,
        expires_in_second: int = 60 * 60,
        **context: Any
    ) -> Dict[str, str]:
        client: S3Client = await get_s3_client()
        bucket = str(owner_id).lower()
        await self._ensure_bucket(client, bucket)

        object_key = build_key(object_kind, **context)

        upload_url = await client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket,
                "Key": object_key,
                "ContentType": content_type.value,
                "ACL": access.value
            },
            ExpiresIn=expires_in_second,
        )

        public_url = f"{S3_ENV.S3_URL}/{bucket}/{object_key}"
        return {
            "upload_url": upload_url,
            "public_url": public_url,
            "bucket": bucket,
            "key": object_key,
        }

    
        
