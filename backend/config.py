import os
import urllib.parse
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field, field_validator


class Settings(BaseSettings):
    # =========================
    # DATABASE (OBRIGATÓRIO EM PRODUÇÃO)
    # =========================
    DATABASE_URL: str = ""

    # =========================
    # WHATSAPP
    # =========================
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "central-transfers-2026"
    ALLOWED_ORIGINS: str = "*"

    # =========================
    # SEGURANÇA & PAGAMENTOS (Configurar no .env)
    # =========================
    SECRET_KEY: str = "mudar_em_producao_pelo_menos_32_caracteres"
    MERCADO_PAGO_ACCESS_TOKEN: str = ""

    # =========================
    # CONFIG
    # =========================
    APP_VERSION: str = "1.0.0"

    @computed_field
    @property
    def database_url(self) -> str:
        """Retorna a URL de conexão focada em PostgreSQL/Aiven."""
        if not self.DATABASE_URL or "SUA_SENHA" in self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL não configurada corretamente no .env")

        url = self.DATABASE_URL.strip()

        # Garante o driver psycopg (v3) substituindo tanto postgres:// quanto postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://") and "+psycopg" not in url:
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)

        # Garante SSL para Aiven
        if "sslmode" not in url:
            sep = "&" if "?" in url else "?"
            url += f"{sep}sslmode=require"

        return url

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
