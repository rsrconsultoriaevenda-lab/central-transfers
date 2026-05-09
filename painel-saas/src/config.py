from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "central-transfers"
    ENV: str = "development"

    # Security
    ADMIN_EMAIL: str = "rsrconsultoriaevenda@gmail.com"
    ADMIN_PASS: str = "Ren@220382"
    VALIDATION_MODE: bool = False

    SECRET_KEY: str = "SEU_SEGREDO_SUPER_FORTE"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Database
    DATABASE_URL: str = "sqlite:///./test.db"
    DB_HOST: Optional[str] = None
    DB_PORT: Optional[int] = None
    DB_USER: Optional[str] = None
    DB_PASSWORD: Optional[str] = None
    DB_NAME: Optional[str] = None

    # Mercado Pago
    MERCADO_PAGO_ACCESS_TOKEN: Optional[str] = None
    MERCADO_PAGO_WEBHOOK_SECRET: Optional[str] = None

    # WhatsApp (Meta API)
    WHATSAPP_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_API_VERSION: str = "v20.0"
    WHATSAPP_VERIFY_TOKEN: str = "central_secret_token"
    WHATSAPP_APP_SECRET: Optional[str] = None

    # Sentry (Opcional, mas recomendado para Go-Live)
    SENTRY_DSN: Optional[str] = None

    # Frontend URL (for redirects)
    FRONTEND_URL: str = "http://localhost:5173"

    # CORS
    ALLOWED_ORIGINS: str = "*"  # Deve ser restrito no .env de produção

    # Cloudinary
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None

    # Email SMTP
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: Optional[int] = None
    SMTP_USER: Optional[str] = None
    SMTP_PASS: Optional[str] = None


settings = Settings()
