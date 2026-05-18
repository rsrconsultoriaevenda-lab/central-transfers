import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Infraestrutura Base
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "CENTRAL_TRANSFERS_SUPER_SECRET_KEY_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # Integração Cloudinary (Lidas automaticamente do painel do Railway ou .env)
    CLOUDINARY_CLOUD_NAME: str = os.getenv("CLOUDINARY_CLOUD_NAME", "")
    CLOUDINARY_API_KEY: str = os.getenv("CLOUDINARY_API_KEY", "")
    CLOUDINARY_API_SECRET: str = os.getenv("CLOUDINARY_API_SECRET", "")

class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"

    # =====================================================================
    # Exportação global protegida
    # =====================================================================
settings = Settings()
Settings = Settings