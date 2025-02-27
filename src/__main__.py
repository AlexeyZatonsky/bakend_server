import uvicorn

from .settings.config import settings
                          


if __name__ == '__main__':

    uvicorn.run(
        'src.app:app',
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=True,
    )