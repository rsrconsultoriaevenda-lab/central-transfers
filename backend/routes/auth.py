from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.auth import verificar_senha, criar_token, get_usuario_atual

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/login", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """
    Endpoint de autenticação. Verifica as credenciais e retorna um token JWT.
    """
    # Busca o usuário pelo e-mail fornecido
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == request.email).first()

    # Valida se o usuário existe e se a senha está correta
    if not usuario or not verificar_senha(request.senha, usuario.senha):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos"
        )

    # Gera o token de acesso incluindo as claims de identidade e permissão
    access_token = criar_token(dados={
        "sub": usuario.email,
        "user_id": usuario.id,
        "role": usuario.role
    })

    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UsuarioResponse)
def get_me(current_user: dict = Depends(get_usuario_atual)):
    """
    Retorna os dados do usuário autenticado. 
    Essencial para o frontend validar a sessão e identificar o papel (role) do usuário.
    """
    return current_user
