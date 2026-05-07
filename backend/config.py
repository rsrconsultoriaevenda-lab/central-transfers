import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Central Transfers API"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "chave-temporaria-para-deploy")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7 dias
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    class Config:
        case_sensitive = True

settings = Settings()
