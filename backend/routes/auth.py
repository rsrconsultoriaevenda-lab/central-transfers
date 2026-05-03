from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.auth import verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    # 1. Busca o usuário pelo e-mail
    usuario = db.query(models.Usuario).filter(models.Usuario.email == request.email).first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    
    # 2. Verifica a senha usando o hash seguro
    if not verificar_senha(request.senha, usuario.senha):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos")
    
    # 3. Cria o payload do token com dados do SaaS
    token_data = {
        "sub": usuario.email,
        "user_id": usuario.id,
        "empresa_id": usuario.empresa_id,
        "role": usuario.role
    }
    
    access_token = criar_token(token_data)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": usuario.role
    }