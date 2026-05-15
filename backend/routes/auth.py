from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.auth import verificar_senha, criar_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/login")
def login(
    request: schemas.LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Realiza login e retorna JWT.
    """

    # 1. Busca o usuário pelo e-mail
    user = db.query(models.Usuario).filter(
        models.Usuario.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )

    # 2. Verifica a senha (certifique-se que o schema LoginRequest usa o campo 'senha')
    senha_valida = verificar_senha(
        request.senha,
        user.senha_hash
    )

    if not senha_valida:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Senha inválida"
        )

    # 3. Verifica se o usuário está ativo
    if not user.ativo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário desativado"
        )

    # 4. Gera os dados para o token e cria o JWT
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role
    }

    access_token = criar_token(dados=token_data)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
