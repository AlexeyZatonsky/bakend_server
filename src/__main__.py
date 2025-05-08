import logging
import uvicorn
from .settings.config import API_ENV
from .core.log import configure_logging

logger = logging.getLogger("src.main")
configure_logging()

if __name__ == '__main__':
    configure_logging()
    
    logger.debug("Запуск приложения")

    uvicorn.run(
        'src.app:app',
        host=API_ENV.SERVER_HOST,
        port=API_ENV.SERVER_PORT,
        reload=True,
    )
