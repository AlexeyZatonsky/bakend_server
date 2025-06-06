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
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 999999

class APIEnv(BaseSettings):
    SERVER_HOST: str
    SERVER_PORT: int
    API_PATH: str = "api"
    BASE_SERVER_URL: str
    FRONTEND_PORT: str = "5173"
    FRONTEND_TESTER_IP: str
    
    @property
    def public_url(self) -> str:
        return f"{self.BASE_SERVER_URL}/{self.API_PATH}"
    
    @property
    def frontend_url(self) -> str:
        return f"http://{self.BASE_SERVER_URL}:{self.FRONTEND_PORT}"
    
    @property
    def frontend_tester_url(self) -> str:
        return f"http://{self.frontend_tester_url}:{self.FRONTEND_PORT}"

class S3Env(BaseSettings):
    S3_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    S3_PUBLIC_URL: str
    BASE_SERVER_URL: str
    MINIO_PATH: str = "minio"
    
    @property
    def public_url(self) -> str:
        return f"{self.BASE_SERVER_URL}/{self.MINIO_PATH}"

class WebhookEnv(BaseSettings):
    MINIO_WEBHOOK_ENDPOINT: str
    MINIO_WEBHOOK_TOKEN: str


API_ENV = APIEnv()
DB_ENV = DBEnv()
S3_ENV = S3Env()
MODE_ENV = ModeEnv()
AUTH_ENV = AuthEnv()
WEBHOOK_ENV = WebhookEnv()