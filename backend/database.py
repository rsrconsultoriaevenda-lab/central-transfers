import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

logger = logging.getLogger(__name__)

db_url = settings.database_url

if not db_url:
    logger.error(
        "❌ ERRO CRÍTICO: DATABASE_URL não foi carregada corretamente no sistema!")
else:
    safe_url = db_url.split("@")[-1] if "@" in db_url else "URL Malformada"
    logger.info(f"📡 Tentando conexão com o banco em: {safe_url}")

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_recycle=300
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
