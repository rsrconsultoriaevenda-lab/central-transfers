import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Define a pasta raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # --- APP INFO ---
    APP_NAME: str = "Central Transfers API"
    ENV: str = "development"
    ADMIN_EMAIL: str = "rsrconsultoriaevenda@gmail.com"

    # --- SEGURANÇA ---
    SECRET_KEY: str = "chave-temporaria-dev-mude-em-producao"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    # --- BANCO DE DADOS ---
    DATABASE_URL: str = "postgresql+psycopg2://avnadmin:AVNS_YKoUmfA9pYTK3wIupNn@central-transfers-central-transfers.c.aivencloud.com:16880/defaultdb?sslmode=require"

    # --- INTEGRAÇÕES: PAGAMENTO ---
    MERCADO_PAGO_ACCESS_TOKEN: str = ""
    MERCADO_PAGO_WEBHOOK_SECRET: str = ""

    # --- INTEGRAÇÕES: WHATSAPP ---
    EVOLUTION_URL: str = ""
    EVOLUTION_API_KEY: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "central_S-14"

    # --- INTEGRAÇÕES: NOTIFICAÇÕES PUSH ---
    VAPID_PUBLIC_KEY: str = ""
    VAPID_PRIVATE_KEY: str = ""
    VAPID_MAILTO: str = "suporte@centraltransfers.com"

    # --- INTEGRAÇÕES: E-MAIL (SMTP) ---
    SMTP_USER: str = ""
    SMTP_PASS: str = ""
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587

    # --- INTEGRAÇÕES: CLOUDINARY ---
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    # --- FRONTEND ---
    FRONTEND_URL: str = "http://localhost:5173"
    ALLOWED_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_allowed_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]

        # Instância global #
settings = Settings()