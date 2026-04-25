from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_usuario_atual

router = APIRouter(prefix="/motoristas", tags=["Motoristas"])


@router.get("/", response_model=List[schemas.Motorista])  # type: ignore
def listar(db: Session = Depends(get_db), email: str = Depends(get_usuario_atual)):
    # Proteção: Apenas admin/operador pode listar motoristas
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email).first()
    if not usuario or usuario.role not in ["admin", "operador"]:
        raise HTTPException(
            status_code=403, detail="Acesso negado. Apenas administradores podem ver a lista de motoristas.")

    return db.query(models.Motorista).all()


@router.post("/")
def criar(motorista: schemas.Motorista, db: Session = Depends(get_db), current_user: str = Depends(get_usuario_atual)):
    try:
        novo = models.Motorista(**motorista.model_dump(exclude={"id"}))
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
