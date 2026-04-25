import os
import certifi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.config import settings

connect_args = {}
# O Aiven exige SSL para conexões seguras.
# Se a URL contiver o host da Aiven, ativamos o SSL apontando para o certificado.
if "aivencloud.com" in settings.full_database_url:
    connect_args["ssl"] = {
        "ca": certifi.where(),
        "check_hostname": False  # Evita erros de handshake em alguns ambientes de nuvem
    }

engine = create_engine(  # type: ignore
    settings.full_database_url,
    pool_pre_ping=True,
    connect_args=connect_args
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
