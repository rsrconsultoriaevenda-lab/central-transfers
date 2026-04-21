from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_current_user

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.get("/", response_model=List[schemas.Cliente])
def listar_clientes(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
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
