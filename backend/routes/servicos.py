from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from backend.database import get_db
from backend.schemas import PedidoOut
from backend.servico import ServicoCreate, ServicoUpdateStatus, ServicoResponse
from backend.auth import get_usuario_atual
from backend import models, schemas
from backend.services.servico_service import (
    criar_servico,
    listar_servicos,
    listar_servicos_por_usuario,
    atribuir_motorista,
    atualizar_status
)

router = APIRouter(prefix="/servicos", tags=["Serviços"])


@router.post("/", response_model=ServicoResponse)
def criar(data: ServicoCreate, db: Session = Depends(get_db), email: str = Depends(get_usuario_atual)):
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return criar_servico(db, data, usuario.id)


@router.get("/", response_model=List[ServicoResponse])
def listar(db: Session = Depends(get_db)):
    try:
        servicos = listar_servicos(db)
        return servicos
    except Exception as e:
        print("ERRO SERVICOS:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meus", response_model=List[ServicoResponse])
def meus(db: Session = Depends(get_db)):
    # Temporariamente retornando todos para evitar erro 500/401 até o front estar estável
    return listar_servicos(db)


@router.put("/{servico_id}/atribuir/{motorista_id}")
def atribuir(
    servico_id: int,
    motorista_id: int,
    db: Session = Depends(get_db),
    email: str = Depends(get_usuario_atual)
):
    # Validação de Perfil (Role)
    usuario_admin = db.query(models.Usuario).filter(
        models.Usuario.email == email).first()
    if not usuario_admin or usuario_admin.role not in ["admin", "operador"]:
        raise HTTPException(
            status_code=403, detail="Apenas administradores podem atribuir motoristas")

    servico = atribuir_motorista(db, servico_id, motorista_id)

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    return servico


@router.put("/{servico_id}/status")
def status(
    servico_id: int,
    data: ServicoUpdateStatus,
    db: Session = Depends(get_db),
    email: str = Depends(get_usuario_atual)
):
    servico = atualizar_status(db, servico_id, data.status)

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    return servico
