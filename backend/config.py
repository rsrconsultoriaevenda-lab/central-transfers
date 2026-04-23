from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import computed_field

class Settings(BaseSettings):
    # Configurações do Banco de Dados
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "123456"
    DB_NAME: str = "central_transfers"

    # Configurações da API do WhatsApp (Meta)
    WHATSAPP_TOKEN: str = ""
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_API_VERSION: str = "v20.0"
    WHATSAPP_VERIFY_TOKEN: str = "central_secret_token"

    @computed_field
    @property
    def database_url(self) -> str:
        """Gera a string de conexão para o SQLAlchemy a partir dos campos individuais."""
        return f"mysql+mysqlconnector://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(
        env_file="backend/.env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()