from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_usuario_atual

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=List[schemas.Cliente])  # type: ignore
def listar_clientes(db: Session = Depends(get_db), email: str = Depends(get_usuario_atual)):
    # Proteção: Apenas admin/operador pode listar clientes
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email).first()
    if not usuario or usuario.role not in ["admin", "operador"]:
        raise HTTPException(
            status_code=403, detail="Acesso negado. Apenas administradores podem ver a lista de clientes.")

    return db.query(models.Cliente).all()


@router.post("/")
def criar_cliente(cliente: schemas.Cliente, db: Session = Depends(get_db)):
    try:
        novo = models.Cliente(**cliente.model_dump(exclude={"id"}))
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
