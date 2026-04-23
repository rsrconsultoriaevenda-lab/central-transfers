import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 🔐 Carrega a URL do banco a partir das variáveis de ambiente (Render)
DATABASE_URL = os.getenv("DATABASE_URL")

# 🚨 Validação obrigatória
if not DATABASE_URL:
    raise Exception("DATABASE_URL não definida nas variáveis de ambiente")

# 🔧 Garante compatibilidade com SQLAlchemy + MySQL Connector
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+mysqlconnector://")

    # 🚀 Cria a engine com suporte a conexão estável (Aiven exige SSL)
    engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,
        pool_recycle=300
    )

    # 🧠 Cria sessão do banco
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )

    # 🧱 Base para os modelos
    Base = declarative_base()


    # 🔄 Dependency para uso nas rotas
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()