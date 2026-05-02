from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from backend.database import get_db
from backend.schemas import PedidoOut
from backend.servico import ServicoUpdateStatus, ServicoResponse
from backend.auth import get_usuario_atual
from backend import models, schemas
from backend.database import tenant_id
from backend.services.servico_service import (
    criar_servico,
    listar_servicos,
    listar_servicos_por_usuario,
    atualizar_status
)

router = APIRouter(prefix="/servicos", tags=["Serviços"])


@router.post("/", response_model=ServicoResponse)
async def criar_servico_route(
    nome: str = Form(...),
    categoria: str = Form(...),
    valor: float = Form(...),
    descricao: str = Form(...),
    imagem: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    # Não precisamos mais buscar o usuário nem setar o empresa_id manualmente.
    # O Hook no database.py fará isso automaticamente usando o ContextVar.
    from backend.schemas import Servico
    data_obj = Servico(
        nome=nome,
        categoria=categoria,
        valor=valor,
        descricao=descricao
    )
    return criar_servico(db, data_obj, user["id"])


@router.get("/", response_model=List[ServicoResponse])
def listar_servicos_route(db: Session = Depends(get_db), user=Depends(get_usuario_atual)):
    try:
        # O Hook no database.py aplicará o filtro de empresa_id automaticamente aqui
        servicos = db.query(models.Servico).all()
        return servicos
    except Exception as e:
        print("ERRO SERVICOS:", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/meus", response_model=List[ServicoResponse])
def meus(db: Session = Depends(get_db)):
    # Temporariamente retornando todos para evitar erro 500/401 até o front estar estável
    return listar_servicos(db)


@router.put("/{servico_id}/status")
def atualizar_status_servico(
    servico_id: int,
    data: ServicoUpdateStatus,
    db: Session = Depends(get_db),
    email: str = Depends(get_usuario_atual)
):
    servico = atualizar_status(db, servico_id, data.status)

    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    return servico
