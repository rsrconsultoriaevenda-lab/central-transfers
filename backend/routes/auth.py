from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.auth import hash_senha, verificar_senha, criar_token, get_usuario_atual

router = APIRouter(prefix="/auth", tags=["Autenticação"])


class LoginRequest(schemas.BaseModel):
    email: str
    senha: str


@router.post("/register")
def register(email: str, senha: str, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email).first()

    if usuario:
        raise HTTPException(status_code=400, detail="Usuário já existe")

    novo_usuario = models.Usuario(
        email=email,
        senha=hash_senha(senha)
    )

    db.add(novo_usuario)
    db.commit()

    return {"msg": "Usuário criado com sucesso"}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == data.email).first()

    if not usuario or not verificar_senha(data.senha, usuario.senha):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    token = criar_token({"sub": usuario.email})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UsuarioResponse)
def read_users_me(db: Session = Depends(get_db), email_usuario: str = Depends(get_usuario_atual)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email_usuario).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario
