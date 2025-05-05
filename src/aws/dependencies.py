from typing import Any
from types_aiobotocore_s3.client import S3Client

from botocore.exceptions import ClientError

from .key_strategies import ObjectKind, _STRATEGY_REGISTRY




import logging
from ..core.log import configure_logging



logger = logging.getLogger(__name__)
configure_logging()


def build_object_key(object_kind: ObjectKind, **context: Any) -> str:
    """Return S3 key according to strategy registered for *object_kind*."""
    try:
        strategy = _STRATEGY_REGISTRY[object_kind]
    except KeyError as exc:  # pragma: no cover
        raise ValueError(f"No strategy registered for {object_kind!r}") from exc
    return strategy.build_key(**context)


async def _ensure_bucket(client: S3Client, bucket_name: str) -> None:    
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
    


