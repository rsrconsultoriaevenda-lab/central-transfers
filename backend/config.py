import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field


class Settings(BaseSettings):
    # =========================
    # 🔐 DATABASE (PRIORIDADE: ENV)
    # =========================
    # Preferencialmente, defina a DATABASE_URL completa no Render.
    DATABASE_URL: str = ""

    # Fallback para desenvolvimento local ou se DATABASE_URL não for fornecida
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", 3306))
    DB_USER: str = os.getenv("DB_USER", "root")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "123456")
    DB_NAME: str = os.getenv("DB_NAME", "central_transfers")

    # =========================
    # 📲 WHATSAPP
    # =========================
    WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
    PHONE_NUMBER_ID: str = os.getenv("PHONE_NUMBER_ID", "")
    WHATSAPP_VERIFY_TOKEN: str = os.getenv("WHATSAPP_VERIFY_TOKEN", "central_secret_token")

    # =========================
    # 🔗 DATABASE URL FINAL (Propriedade computada)
    # =========================
    @computed_field
    @property
    def full_database_url(self) -> str:
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=[".env", "backend/.env"],
        env_file_encoding="utf-8",
        extra="ignore"
    )
settings = Settings()
