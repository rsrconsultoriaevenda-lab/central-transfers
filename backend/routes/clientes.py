from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend import models, schemas
from backend.auth import get_usuario_atual

router = APIRouter(prefix="/clientes", tags=["Clientes"])


# ==============================
# LISTAR CLIENTES
# ==============================
@router.get("/", response_model=List[schemas.Cliente])
def listar_clientes(
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    if user.get("role") not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    return db.query(models.Cliente).all()


# ==============================
# CRIAR CLIENTE
# ==============================
@router.post("/", response_model=schemas.Cliente)
def criar_cliente(  # Indentação corrigida
    cliente: schemas.Cliente,
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    if user.get("role") not in ["admin", "operador"]:
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        novo = models.Cliente(
            nome=cliente.nome,
            telefone=cliente.telefone,
            email=cliente.email
        )

        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
