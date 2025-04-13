import logging
import uvicorn
from .settings.config import settings
from .core.log import configure_logging

logger = logging.getLogger("src.main")
configure_logging()

if __name__ == '__main__':
    configure_logging()
    
    logger.debug("Запуск приложения")

    uvicorn.run(
        'src.app:app',
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )
