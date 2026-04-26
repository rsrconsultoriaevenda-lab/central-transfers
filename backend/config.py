import os
import urllib.parse
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, field_validator


class Settings(BaseSettings):
    # =========================
    # DATABASE (OBRIGATÓRIO EM PRODUÇÃO)
    # =========================
    DATABASE_URL: str | None = None

    # Fallback para desenvolvimento local
    DB_HOST: str = "localhost"
    DB_PORT: int = 16880
    DB_USER: str = "avnadmin"
    DB_PASSWORD: str = ""
    DB_NAME: str = "defaultdb"

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

    @computed_field
    @property
    def database_url(self) -> str:
        # Se DATABASE_URL existir e não for apenas espaços em branco
        if self.DATABASE_URL and str(self.DATABASE_URL).strip():
            url = str(self.DATABASE_URL).strip()
            
            if "postgres" in url or ":16880" in url:
                # Remove parâmetros da query e força o driver postgresql+psycopg2
                clean_body = url.split("://")[-1].split("?")[0]
                return f"postgresql+psycopg2://{clean_body}?sslmode=require"
            
            # Identifica se é MySQL
            if "mysql" in url:
                clean_body = url.split("://")[-1].split("?")[0]
                return f"mysql+pymysql://{clean_body}"

            return url

        # Codifica o usuário e a senha para evitar problemas com caracteres especiais (@, #, :, /)
        user = urllib.parse.quote_plus(self.DB_USER)
        password = urllib.parse.quote_plus(self.DB_PASSWORD)
        # Fallback atualizado para PostgreSQL
        return f"postgresql+psycopg2://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
