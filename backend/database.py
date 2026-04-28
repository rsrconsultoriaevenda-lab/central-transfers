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
    # Loga apenas o host para segurança, ocultando usuário e senha
    host_part = db_url.split("@")[-1] if "@" in db_url else "URL"
    logger.info(f"📡 Iniciando engine de banco de dados: {host_part}")

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,            # Mantém 5 conexões prontas
    max_overflow=10,        # Permite até 10 extras em pico
    pool_timeout=30         # Espera 30s antes de dar timeout
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
