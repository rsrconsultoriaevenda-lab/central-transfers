from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from typing import Optional
from backend.config import settings

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_usuario_atual(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[ALGORITHM])
        email = payload.get("sub")

        if email is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        return email

    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def criar_token(dados: dict):
    dados_copia = dados.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    dados_copia.update({"exp": expire})

    token = jwt.encode(dados_copia, settings.SECRET_KEY, algorithm=ALGORITHM)
    return token


def hash_senha(senha: str):
    return pwd_context.hash(senha)


def verificar_senha(senha: str, senha_hash: str):
    return pwd_context.verify(senha, senha_hash)
