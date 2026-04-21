from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_current_user

router = APIRouter(prefix="/motoristas", tags=["Motoristas"])


@router.get("/", response_model=List[schemas.Motorista])
def listar(db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    return db.query(models.Motorista).all()


@router.post("/")
def criar(motorista: schemas.Motorista, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    try:
        novo = models.Motorista(**motorista.dict(exclude={"id"}))
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
