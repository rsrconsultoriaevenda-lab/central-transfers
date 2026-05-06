from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_usuario_atual

router = APIRouter(prefix="/servicos", tags=["Serviços"])


@router.get("/")
def listar_servicos(db: Session = Depends(get_db)):
    return db.query(models.Servico).all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ServicoResponse)
def criar_servico(servico: schemas.Servico, db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    novo = models.Servico(**servico.model_dump(exclude={"id"}))
    db.add(novo)
    db.commit()
    db.refresh(novo)
    return novo
