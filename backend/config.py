import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # O Railway injeta a string do PostgreSQL aqui automaticamente.
    # Se rodar local, ele usa o SQLite "test.db".
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test.db"
    )

    SECRET_KEY: str = os.getenv("SECRET_KEY", "CENTRAL_TRANSFERS_SUPER_SECRET_KEY_2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

class Config:
    env_file = ".env"
    env_file_encoding = "utf-8"

    # =====================================================================
    # AS LINHAS ABAIXO PRECISAM FICAR COLADAS NA ESQUERDA (ESCOPO GLOBAL)
    # =====================================================================
settings = Settings()  # Atende quem importa minúsculo
Settings = Settings   # Atende quem tenta instanciar ou usar como classe