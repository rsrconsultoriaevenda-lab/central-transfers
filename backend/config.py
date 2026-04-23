from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field
import os


class Settings(BaseSettings):
    # =========================
    # 🔐 DATABASE (PRIORIDADE: ENV)
    # =========================
    DATABASE_URL: str | None = None

    # Fallback local (DEV)
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "central_transfers"

    # =========================
    # 📲 WHATSAPP
    # =========================
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_API_VERSION: str = "v20.0"
    WHATSAPP_VERIFY_TOKEN: str = "central_secret_token"

    # =========================
    # 🔗 DATABASE URL FINAL
    # =========================
    @computed_field
    @property
    def database_url(self) -> str:
        # 👉 PRODUÇÃO (Render / Aiven)
        if self.DATABASE_URL:
            return self.DATABASE_URL

        # 👉 LOCAL (fallback)
        return (
        f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
        f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    )

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


    settings = Settings()