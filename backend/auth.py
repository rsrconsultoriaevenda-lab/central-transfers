from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from backend import models, schemas, database
import os

router = APIRouter(tags=["Autenticação"])

# Chave secreta carregada do ambiente para segurança máxima
SECRET_KEY = os.getenv(
    "JWT_SECRET", "chave-temporaria-para-desenvolvimento-local")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 600

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.Usuario).filter(
        models.Usuario.username == form_data.username).first()
    if not user or not pwd_context.verify(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=400, detail="Usuário ou senha incorretos")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/usuarios", status_code=201)
def criar_usuario(user: schemas.UsuarioCreate, db: Session = Depends(database.get_db)):
    hashed = pwd_context.hash(user.password)
    novo_usuario = models.Usuario(
        username=user.username, hashed_password=hashed)
    db.add(novo_usuario)
    db.commit()
    return {"detail": "Usuário criado"}


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(models.Usuario).filter(
        models.Usuario.username == username).first()
    if user is None:
        raise HTTPException(status_code=401, detail="Usuário inexistente")
    return user
