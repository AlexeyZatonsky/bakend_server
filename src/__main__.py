import uvicorn

from .settings.config import SERVER_HOST, SERVER_PORT



if __name__ == '__main__':

    uvicorn.run(
        'src.app:app',
        host=SERVER_HOST,
        port=int(SERVER_PORT),
        reload=True,
    )