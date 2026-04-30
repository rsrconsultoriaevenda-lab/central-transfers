import os
from pydantic_settings import BaseSettings
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    APP_NAME: str = "central-transfers"
    ENV: str = "production"
    SECRET_KEY: str = "placeholder_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    DATABASE_URL: str = ""
    MERCADO_PAGO_ACCESS_TOKEN: str = ""
    MERCADO_PAGO_WEBHOOK_SECRET: str = ""
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_API_VERSION: str = "v20.0"
    WHATSAPP_VERIFY_TOKEN: str = ""
    ALLOWED_ORIGINS: str = "*"

    model_config = {
        "env_file": str(BASE_DIR / ".env"),
        "extra": "ignore",
        "case_sensitive": False
    }

    # ESTA LINHA DEVE FICAR COLADA NA MARGEM ESQUERDA
settings = Settings()