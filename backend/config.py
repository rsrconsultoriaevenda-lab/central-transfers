from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import List

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "central-transfers"

    ENV: str = "production"

    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    DATABASE_URL: str

    ALLOWED_ORIGINS: str = "*"

    # WebSocket / realtime config (adicionado no último commit)
    WEBSOCKET_ENABLED: bool = True

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_allowed_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",")]


        settings = Settings()