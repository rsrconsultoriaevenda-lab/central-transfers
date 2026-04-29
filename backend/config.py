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

        # Lógica para PostgreSQL
        if url.startswith("postgres://") or url.startswith("postgresql://"):
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql+psycopg2://", 1)
            elif "+psycopg2" not in url:
                url = url.replace("postgresql://", "postgresql+psycopg2://", 1)

            if "sslmode" not in url:
                url += ("&" if "?" in url else "?") + "sslmode=require"
        # Detecta e corrige o driver para MySQL (Railway)
        elif url.startswith("mysql://"):
            url = url.replace("mysql://", "mysql+pymysql://", 1)

        return url

    @computed_field
    @property
    def cors_origins(self) -> list[str]:
        """Converte a string de origens em uma lista limpa para o middleware."""
        if not self.ALLOWED_ORIGINS or self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
