from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from backend.database import get_db
from backend.schemas import PedidoOut
from backend.servico import ServicoUpdateStatus, ServicoResponse
from backend.auth import get_usuario_atual
from backend import models, schemas
from backend.services.image_service import upload_image_to_cloudinary
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
    # Lógica de Upload para Cloudinary
    imagem_url = None
    if imagem:
        try:
            imagem_url = await upload_image_to_cloudinary(imagem)
        except Exception as e:
            print(f"Erro ao fazer upload para Cloudinary: {e}")
            # Você pode optar por lançar um erro ou continuar sem imagem

    from backend.schemas import Servico
    data_obj = Servico(
        nome=nome,
        categoria=categoria,
        valor=valor,
        descricao=descricao,
        imagem_url=imagem_url
    )
    return criar_servico(db, data_obj, user["id"])


@router.get("/disponibilidade/datas-bloqueadas")
def obter_datas_bloqueadas(db: Session = Depends(get_db)):
    """
    Retorna datas onde a frota está completa (Pedidos >= Motoristas Ativos).
    """
    try:
        # 1. Conta motoristas ativos (Capacidade Total)
        capacidade_total = db.query(models.Motorista).filter(models.Motorista.status == 'ATIVO').count()
        if capacidade_total == 0:
            capacidade_total = 10 # Fallback para sua frota inicial

        # 2. Agrupa pedidos por data e conta
        # Filtramos apenas pedidos confirmados (PAGO, ACEITO, CONCLUIDO)
        pedidos_por_dia = db.query(
            func.date(models.Pedido.data_servico).label('data'),
            func.count(models.Pedido.id).label('total')
        ).filter(
            models.Pedido.status.in_(['PAGO', 'ACEITO', 'CONCLUIDO'])
        ).group_by(func.date(models.Pedido.data_servico)).all()

        # 3. Identifica datas que atingiram a capacidade
        bloqueadas = [p.data.isoformat() for p in pedidos_por_dia if p.total >= capacidade_total]
        
        return {"bloqueadas": bloqueadas}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


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
