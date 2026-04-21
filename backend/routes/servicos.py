from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_current_user

router = APIRouter(prefix="/servicos", tags=["Serviços"])


@router.get("/", response_model=List[schemas.Servico])
def listar(db: Session = Depends(get_db)):
    return db.query(models.Servico).all()


@router.post("/")
def criar(servico: schemas.Servico, db: Session = Depends(get_db), current_user: models.Usuario = Depends(get_current_user)):
    try:
        novo = models.Servico(**servico.dict(exclude={"id"}))
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
