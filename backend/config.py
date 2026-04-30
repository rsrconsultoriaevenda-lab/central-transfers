from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

# Define o diretório base para localizar o arquivo .env
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # Configurações Gerais
    APP_NAME: str = "central-transfers"
    ENV: str = "production"

    # Segurança
    SECRET_KEY: str = "placeholder_key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Banco de Dados e Integrações
    DATABASE_URL: str = ""
    MERCADO_PAGO_ACCESS_TOKEN: str = ""
    MERCADO_PAGO_WEBHOOK_SECRET: str = ""

    # WhatsApp API
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_API_VERSION: str = "v20.0"
    WHATSAPP_VERIFY_TOKEN: str = ""

    # CORS
    ALLOWED_ORIGINS: str = "*"

    # Configurações do Pydantic (V2)
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        extra="ignore",
        case_sensitive=False
    )

    # ESTA LINHA DEVE FICAR COLADA NA MARGEM ESQUERDA
    # Fora do bloco 'class' para que o Python reconheça a classe já definida
settings = Settings()