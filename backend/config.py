import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # O Pydantic lerá automaticamente a variável DATABASE_URL injetada pelo Railway.
    # Caso esteja rodando local, ele usará o SQLite local "test.db".
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

    # Inicialização da instância global de configurações
    settings = Settings()