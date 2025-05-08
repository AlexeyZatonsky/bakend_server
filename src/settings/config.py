from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict



load_dotenv()

class ModeEnv(BaseSettings):
    MODE: str

class DBEnv(BaseSettings):
    DB_USER: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_PASS: str
    @property   
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

class AuthEnv(BaseSettings):
    SECRET_AUTH: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

class APIEnv(BaseSettings):
    SERVER_HOST: str
    SERVER_PORT: int


class S3Env(BaseSettings):
    S3_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    

    
API_ENV = APIEnv()
DB_ENV = DBEnv()
S3_ENV = S3Env()
MODE_ENV = ModeEnv()
AUTH_ENV = AuthEnv()