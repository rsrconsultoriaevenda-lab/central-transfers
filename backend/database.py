import os
from contextvars import ContextVar
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Query, Mapper
from sqlalchemy.ext.declarative import declarative_base

# Variável global para armazenar o ID da empresa na thread atual da requisição
tenant_id: ContextVar[int] = ContextVar("tenant_id", default=None)

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

# 5. DEPENDENCY (Usada nas rotas FastAPI)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# HOOK DE MULTITENANCY: Aplica filtro de empresa_id automaticamente
@event.listens_for(Query, "before_compile", retval=True)
def before_compile_tenant_filter(query):
    """
    Intercepta a query antes da compilação.
    Se houver um tenant_id definido no contexto, aplica o filtro em todas as entidades
    que possuem o atributo 'empresa_id'.
    """
    tid = tenant_id.get()
    if tid is not None:
        for desc in query.column_descriptions:
            entity = desc['entity']
            if entity and hasattr(entity, 'empresa_id'):
                query = query.filter(entity.empresa_id == tid)
    return query


@event.listens_for(Mapper, "before_insert")
def before_insert_tenant_id(mapper, connection, target):
    """
    Hook para inserir automaticamente o empresa_id em novos registros.
    """
    tid = tenant_id.get()
    if tid is not None and hasattr(target, 'empresa_id'):
        # Definimos o ID apenas se ele ainda não estiver preenchido
        if getattr(target, "empresa_id") is None:
            setattr(target, "empresa_id", tid)
