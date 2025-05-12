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
            logger.debug(f"Создан новый бакет: {bucket_name}")
        except (
            client.exceptions.BucketAlreadyOwnedByYou,  
            client.exceptions.BucketAlreadyExists,      
        ):
            logger.debug(f"Бакет с именем {bucket_name} уже создан")
        except ClientError:
            logger.error(f"Ошибка при создании бакета {bucket_name}")
            raise
        
        # Настраиваем уведомления очень простым способом, без фильтров
        try:
            await client.put_bucket_notification_configuration(
                Bucket=bucket_name,
                NotificationConfiguration={
                    "QueueConfigurations": [
                        {
                            "Id": "webhook-config",
                            "QueueArn": "arn:minio:sqs::webhook:webhook",
                            "Events": ["s3:ObjectCreated:*"]
                        }
                    ]
                }
            )
        except Exception as e:
            logger.warning(f"Не удалось настроить уведомления для бакета {bucket_name}: {e}")


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

        # Получаем presigned URL от MinIO с правильной подписью для внутреннего хоста
        internal_url = await client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket,
                "Key": object_key,
                "ContentType": content_type.value,
                "ACL": access.value
            },
            ExpiresIn=expires_in_second,
        )
        
        # Формируем публичный URL для доступа к объекту
        public_url = f"{S3_ENV.public_url}/{bucket}/{object_key}"
        logger.debug(f" публичный URL для доступа к объекту - {public_url}")

        url_parts = internal_url.split('/', 3)
        if len(url_parts) < 4:
            logger.error(f"Неверный формат URL: {internal_url}")
            # Возвращаем оригинальный URL в случае ошибки
            external_upload_url = internal_url.replace(S3_ENV.S3_URL, S3_ENV.BASE_SERVER_URL)
        else:
            # url_parts[3] содержит bucket/key?params...
            path_params = url_parts[3]
            # Формируем новый URL через наш прокси
            external_upload_url = f"{S3_ENV.BASE_SERVER_URL}/s3proxy/{path_params}"
        
        return {
            "upload_url": external_upload_url,  # URL для внешнего доступа
            "public_url": public_url,
            "bucket": bucket,
            "key": object_key,
        }

    def transform_presigned_url(self, internal_url: str) -> str:
        url_parts = internal_url.split('/', 3)
        if len(url_parts) < 4:
            return internal_url.replace(S3_ENV.S3_URL, S3_ENV.BASE_SERVER_URL)
        
        path_params = url_parts[3]
        return f"{S3_ENV.BASE_SERVER_URL}/s3proxy/{path_params}"

    
        
