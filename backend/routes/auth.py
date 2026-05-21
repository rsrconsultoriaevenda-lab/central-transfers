from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend import models, schemas, auth
from backend.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["Autenticação"]
)


@router.post("/login")
def login(
    login_data: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint para autenticação de administradores (Usuario) e motoristas (Motorista).
    """
    # 1. Tenta autenticar como Usuário Administrativo
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == login_data.email
    ).first()

    if usuario and auth.verificar_senha(login_data.senha, usuario.senha_hash):
        # Gera token de acesso para o administrador
        access_token = auth.criar_token(
            dados={"sub": usuario.email, "role": usuario.role}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": usuario.role
        }

    # 2. Tenta autenticar como Motorista
    # Nota: No sistema, motoristas usam o e-mail 'telefone@motorista.com' para login
    motorista = db.query(models.Motorista).filter(
        models.Motorista.email == login_data.email
    ).first()

    if motorista and auth.verificar_senha(login_data.senha, motorista.senha_hash):
        # Gera token de acesso para o motorista
        access_token = auth.criar_token(
            dados={"sub": motorista.email, "role": "motorista"}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "role": "motorista"
        }

    # 3. Se não encontrar nenhum ou a senha for inválida
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="E-mail ou senha incorretos",
        headers={"WWW-Authenticate": "Bearer"},
    )
