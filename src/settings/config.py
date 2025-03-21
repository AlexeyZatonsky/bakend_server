from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict



load_dotenv()

class Settings(BaseSettings):
    MODE: str
    
    DB_USER: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_PASS: str
    
    SECRET_AUTH: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    SERVER_HOST: str
    SERVER_PORT: int

    S3_BUCKET_NAME: str
    S3_URL: str
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    
    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    
    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
