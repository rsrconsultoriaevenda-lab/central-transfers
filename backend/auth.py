from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from backend.config import settings
from backend.database import tenant_id

ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_usuario_atual():
    """
    DESABILITADO TEMPORARIAMENTE: Ignora a validação de token e multitenancy.
    Retorna sempre um perfil de administrador para facilitar os testes.
    """
    # Define o tenant_id como None para que o SQLAlchemy mostre TODOS os dados do banco
    tenant_id.set(None)
    
    return {"email": "admin@centraltransfers.com", "id": 1, "empresa_id": None, "role": "admin"}


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def criar_token(dados: dict):
    dados_copia = dados.copy()
    expire = datetime.now(timezone.utc) + \
        timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_copia.update({"exp": expire})
    return jwt.encode(dados_copia, settings.SECRET_KEY, algorithm=ALGORITHM)


def hash_senha(senha: str):
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)
