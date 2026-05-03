
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db, tenant_id
from backend import models, schemas
from backend.auth import get_usuario_atual, hash_senha
import secrets

router = APIRouter(prefix="/motoristas", tags=["Motoristas"])


@router.get("/", response_model=List[schemas.Motorista])  # type: ignore
def listar(db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    # O Hook de multitenancy no database.py já filtra as queries automaticamente.
    # Apenas verificamos se o usuário logado tem permissão administrativa.
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Acesso negado. Apenas administradores podem ver a lista de motoristas.")

    return db.query(models.Motorista).all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.MotoristaCreateResponse)
def criar(motorista: schemas.MotoristaBase, db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    senha_gerada = None
    try:
        # 1. Criar o registro do Motorista
        novo = models.Motorista(**motorista.model_dump())
        db.add(novo)

        # Flush garante que o objeto seja processado pelos hooks (como o de empresa_id)
        # antes de prosseguirmos para a criação do usuário.
        db.flush()

        # 2. Automação: Criar um Usuário de acesso para este motorista
        # Usamos o telefone como base para o login (ex: 54999999999@motorista.com)
        email_login = f"{motorista.telefone}@motorista.com"

        usuario_existente = db.query(models.Usuario).filter(
            models.Usuario.email == email_login).first()

        if not usuario_existente:
            # Gerar uma senha temporária aleatória
            senha_gerada = secrets.token_urlsafe(8)
            novo_usuario = models.Usuario(
                email=email_login,
                senha=hash_senha(senha_gerada),
                role="motorista",
                empresa_id=tenant_id.get()  # Vincula o motorista ao mesmo ID da empresa do Admin
            )
            db.add(novo_usuario)
            # Em produção, aqui você dispararia um SMS ou E-mail com a senha temporária.
            print(f"ACESSO GERADO: Login {email_login} | Senha {senha_gerada}")

        db.commit()
        db.refresh(novo)
        return {
            "motorista": novo,
            "acesso": {
                "login": email_login,
                "senha": senha_gerada
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{motorista_id}")
def atualizar_plano_motorista(
    motorista_id: int,
    update_data: schemas.MotoristaBase,
    db: Session = Depends(get_db),
    email: str = Depends(get_usuario_atual)
):
    """Atualiza o modelo de cobrança (MENSAL ou MASTER) de um motorista."""
    db_motorista = db.query(models.Motorista).filter(
        models.Motorista.id == motorista_id).first()
    if not db_motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    db_motorista.plano = update_data.plano
    db.commit()
    db.refresh(db_motorista)
    return db_motorista
