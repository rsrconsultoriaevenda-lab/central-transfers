import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. BASE (Sempre no topo)
Base = declarative_base()

# 2. URL do Banco (Busca direta do ENV ou Fallback)
# Isso evita importar o 'settings' e causar ciclos de importação
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# Correção para URLs do SQLAlchemy que começam com postgres:// (comum no Railway)
# O SQLAlchemy 1.4+ exige que seja postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)


# Se estivermos em produção, a URL do banco DEVE vir de uma variável de ambiente
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RENDER"):
    if DATABASE_URL.startswith("sqlite"):
        print("⚠️ AVISO: Usando SQLite em produção. Os dados podem ser perdidos!")

# 3. ENGINE
connect_args = {}
if "postgresql" in DATABASE_URL and "sslmode" not in DATABASE_URL:
    # Garante compatibilidade com bancos gerenciados se não houver param na URL
    connect_args = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

# 4. SESSIONLOCAL (O que o erro diz que não encontra)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
