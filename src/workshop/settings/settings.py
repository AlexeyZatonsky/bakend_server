from pydantic import BaseSettings

from dotenv import load_dotenv
import os



load_dotenv()

DB_HOST = os.environ.get('DB_HOST')
DB_PORT = os.environ.get('DB_PORT')
DB_NAME = os.environ.get('DB_NAME')
DB_USER = os.environ.get('DB_USER')
DB_PASS = os.environ.get('DB_PASS')

SERVER_HOST = os.environ.get('SERVER_HOST')
SERVER_PORT = os.environ.get('SERVER_PORT')


class Settings(BaseSettings):
    server_host: str = SERVER_HOST
    server_port: int = SERVER_PORT
    database_url = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
