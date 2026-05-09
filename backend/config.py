import os
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    APP_NAME: str = "Central Transfers API"

    ENV: str = "development"

    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "chave-temporaria-dev"
    )

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080

    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./test.db"
    )

    # CLOUDINARY
    CLOUDINARY_CLOUD_NAME: str = os.getenv(
        "CLOUDINARY_CLOUD_NAME",
        ""
    )

    CLOUDINARY_API_KEY: str = os.getenv(
        "CLOUDINARY_API_KEY",
        ""
    )

    CLOUDINARY_API_SECRET: str = os.getenv(
        "CLOUDINARY_API_SECRET",
        ""
    )

    ALLOWED_ORIGINS: str = "*"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def get_allowed_origins(self) -> List[str]:
        if self.ALLOWED_ORIGINS == "*":
            return ["*"]

        return [
        o.strip()
        for o in self.ALLOWED_ORIGINS.split(",")
    ]


settings = Settings()