from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv
import os
from backend.config import settings

load_dotenv()

# Correção automática para URLs do Railway/Heroku (postgres:// -> postgresql://)
db_url = settings.DATABASE_URL
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

# Garante SSL para bancos remotos (Aiven/Railway) se não estiver presente na URL
if db_url and "postgresql" in db_url and "sslmode=" not in db_url:
    sep = "&" if "?" in db_url else "?"
    db_url += f"{sep}sslmode=require"

engine = create_engine(
    db_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=(os.getenv("ENV") == "development")
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

naming_convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}

Base = declarative_base(
    metadata=MetaData(naming_convention=naming_convention)
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
