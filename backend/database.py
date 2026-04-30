import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 1. BASE (Sempre no topo)
Base = declarative_base()

# 2. URL do Banco (Busca direta do ENV ou Fallback)
# Isso evita importar o 'settings' e causar ciclos de importação
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

# 3. ENGINE
connect_args = {"sslmode": "require"} if "postgresql" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# 4. SESSIONLOCAL (O que o erro diz que não encontra)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 5. DEPENDENCY
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()