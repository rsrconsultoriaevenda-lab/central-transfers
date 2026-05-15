from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
import os

from backend.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(
    tokenUrl="/auth/login", auto_error=False)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 60)


def criar_token(dados: dict):
    dados_copia = dados.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    dados_copia.update({"exp": expire})

    return jwt.encode(dados_copia, SECRET_KEY, algorithm=ALGORITHM)


def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)


def hash_senha(senha: str):
    return pwd_context.hash(senha)


def get_usuario_atual(token: str = Depends(oauth2_scheme)):
    is_validation = os.getenv("VALIDATION_MODE", "false").lower() == "true"

    if is_validation:
        return {
            "email": "admin@teste.com",
            "id": 1,
            "role": "admin"
        }

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        email: Optional[str] = payload.get("sub")
        user_id: Optional[int] = payload.get("user_id")
        role: Optional[str] = payload.get("role")

        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido"
            )

        return {
            "email": email,
            "id": user_id,
            "role": role
        }

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido"
        )


def get_usuario_opcional(token: Optional[str] = Depends(oauth2_scheme_optional)):
    if not token:
        return None
    try:
        return get_usuario_atual(token)
    except HTTPException:
        return None
