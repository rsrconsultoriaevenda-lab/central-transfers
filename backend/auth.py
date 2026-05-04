from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
import os
from passlib.context import CryptContext
from backend.config import settings
from backend.database import tenant_id

ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_usuario_atual():
    """
    MODO VALIDAÇÃO: Retorna você como a primeira empresa (ID 1).
    Isso ativa os filtros de multitenancy no banco de dados para garantir que
    você veja apenas os seus próprios dados durante a operação real.
    """
    # Verificamos se estamos em modo de teste local ou validação explícita
    is_validation = os.getenv("VALIDATION_MODE", "false").lower() == "true"

    if is_validation:
        tenant_id.set(1)
        return {"email": "rsrconsultoriaevenda@gmail.com", "id": 1, "empresa_id": 1, "role": "admin"}

    # Aqui deveria vir a lógica real de decodificar o JWT Token
    # Por segurança, enquanto não restauramos o código completo de produção:
    raise HTTPException(
        status_code=401, detail="Autenticação real necessária para ambiente público.")


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
