import os
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # =========================
    # DATABASE (OBRIGATÓRIO EM PRODUÇÃO)
    # =========================
    DATABASE_URL: str

    # =========================
    # WHATSAPP
    # =========================
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "central_transfers_token_2024"
    ALLOWED_ORIGINS: str = "*"

    # =========================
    # CONFIG
    # =========================
    APP_VERSION: str = "1.0.0"

    @property
    def database_url(self) -> str:
        """
        Força uso do driver pymysql para suporte a SSL (Aiven/Railway)
        """
        if self.DATABASE_URL and "://" in self.DATABASE_URL:
            return "mysql+pymysql://" + self.DATABASE_URL.split("://")[-1]
        return self.DATABASE_URL

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()