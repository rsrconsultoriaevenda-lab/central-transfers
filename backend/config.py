import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Localiza a raiz do projeto (onde o .env está guardado)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # APP CONFIG
    app_name: str = "central-transfers"
    env: str = "production"

    # SEGURANÇA (O alias garante que ele leia exatamente o nome no .env)
    secret_key: str = Field(..., alias="SECRET_KEY")
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # DATABASE
    database_url: str = Field(..., alias="DATABASE_URL")

    # CORS (Para aceitar requisições da Vercel)
    cors_origins: list = ["*"]

    # Configuração do Pydantic para carregar o arquivo
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False
    )

    settings = Settings()