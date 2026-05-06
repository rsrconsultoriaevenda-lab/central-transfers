from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

# =========================
# CONFIGURAÇÃO JWT
# =========================
SECRET_KEY = "CHANGE_THIS_TO_A_STRONG_SECRET_KEY"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 dia

# =========================
# HASH DE SENHA (BCRYPT)
# =========================
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# endpoint padrão do FastAPI OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# =========================
# SENHAS
# =========================
def verificar_senha(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_senha(password: str) -> str:
    return pwd_context.hash(password)


# =========================
# JWT - CRIAR TOKEN
# =========================
def criar_token(data: dict):
    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


# =========================
# JWT - DECODIFICAR TOKEN
# =========================
def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        user_id: int = payload.get("user_id")
        email: str = payload.get("sub")
        role: str = payload.get("role")

        if user_id is None:
            raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido",
    )

    return {
        "user_id": user_id,
        "email": email,
        "role": role,
    }

    except JWTError:
        raise HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token inválido ou expirado",
)


# =========================
# DEPENDÊNCIA FASTAPI (USER ATUAL)
# =========================
def get_current_user(token: str = Depends(oauth2_scheme)):
    return decode_token(token)


# =========================
# HELPERS DE ROLE (SAA S)
# =========================
def require_role(*allowed_roles: str):
def wrapper(user=Depends(get_current_user)):
    if user["role"] not in allowed_roles:
        raise HTTPException(
    status_code=status.HTTP_403_FORBIDDEN,
    detail="Você não tem permissão para acessar este recurso",
)
return user
    return wrapper