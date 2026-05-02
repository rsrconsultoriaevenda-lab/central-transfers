from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from backend.config import settings
from backend.database import tenant_id

ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_usuario_atual(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY,
                             algorithms=[ALGORITHM])
        email = payload.get("sub")
        user_id = payload.get("user_id")
        # Fallback para o ID do usuário se for o dono
        comp_id = payload.get("empresa_id") or user_id

        if email is None or user_id is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        # Aqui acontece a "mágica": setamos o ID para toda a duração desta requisição
        tenant_id.set(comp_id)

        return {"email": email, "id": user_id, "empresa_id": comp_id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")


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
