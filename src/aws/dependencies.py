from .service import StorageService



import logging
from ..core.log import configure_logging



logger = logging.getLogger(__name__)
configure_logging()


_storage_singleton: StorageService | None = None



async def get_storage_service() -> StorageService:
    logger.debug("инициация storage service")
    global _storage_singleton
    if _storage_singleton is None:
        logger.debug("storage service - none - инициация singleton объекта")
        _storage_singleton = StorageService()
    return _storage_singleton


