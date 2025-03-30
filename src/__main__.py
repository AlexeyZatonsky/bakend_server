import uvicorn
import logging

from .settings.config import settings
                          
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",

)

if __name__ == '__main__':

    uvicorn.run(
        'src.app:app',
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )