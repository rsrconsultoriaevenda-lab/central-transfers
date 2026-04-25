import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, field_validator


class Settings(BaseSettings):
    # =========================
    # 🔐 DATABASE CONFIG
    # =========================
    # No Render, defina DATABASE_URL como: mysql+pymysql://user:pass@host:port/db
    DATABASE_URL: str | None = None

    # Fallback para desenvolvimento local
    DB_HOST: str = "localhost"

    # Validador para evitar o erro "PORT" (converte string suja para int)
    DB_PORT: int = 3306

    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "central_transfers"

    # =========================
    # 📲 WHATSAPP & SECURITY
    # =========================
    WHATSAPP_TOKEN: str = ""
    PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "central_secret_token"
    ALLOWED_ORIGINS: str = "*"

    # Versão da API (útil para logs e manutenção)
    APP_VERSION: str = "1.0.0"

    @field_validator("DB_PORT", mode="before")
    @classmethod
    def parse_db_port(cls, v):
        """Impede o erro de conversão se a env vier como 'PORT' ou vazia"""
        if isinstance(v, str):
            if not v.isdigit(): # Se for 'PORT' ou qualquer texto não numérico
                return 3306
            return int(v)
            return v

            # =========================
            # 🔗 DATABASE URL COMPUTADA
            # =========================
    @computed_field
    @property
    def full_database_url(self) -> str:
        # 1. Prioridade absoluta para DATABASE_URL (padrão Render/Aiven)
        if self.DATABASE_URL and "://" in self.DATABASE_URL:
            # Garante o uso do driver pymysql para suporte a SSL
            raw_url = self.DATABASE_URL.strip()
            # Pega tudo após o :// e força o driver correto
            return "mysql+pymysql://" + raw_url.split("://")[-1]

        # 2. Fallback usando as variáveis individuais (padrão Local)
        return (
        f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@"
        f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    )

    # Configuração do Pydantic para ler arquivos .env automaticamente
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


    settings = Settings()