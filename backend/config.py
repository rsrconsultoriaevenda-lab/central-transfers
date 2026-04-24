import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "")

    model_config = SettingsConfigDict(
        env_file=[".env", "backend/.env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
