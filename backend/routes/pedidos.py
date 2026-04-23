from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_usuario_atual

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("/", response_model=List[schemas.PedidoOut])  # type: ignore
def listar(db: Session = Depends(get_db)):
    return db.query(models.Pedido).options(
        joinedload(models.Pedido.cliente),
        joinedload(models.Pedido.servico),
        joinedload(models.Pedido.motorista)
    ).all()


@router.get("/stats", response_model=schemas.DashboardStats)
def obter_estatisticas(db: Session = Depends(get_db)):
    # Busca contagem aglutinada por status
    stats = db.query(
        models.Pedido.status,
        func.count(models.Pedido.id)
    ).group_by(models.Pedido.status).all()

    stats_dict = {status: count for status, count in stats}

    # Soma do faturamento (apenas pedidos pagos, aceitos ou concluídos)
    faturamento = db.query(func.sum(models.Pedido.valor)).filter(
        models.Pedido.status.in_(["PAGO", "ACEITO", "CONCLUIDO"])
    ).scalar() or 0

    return {
        "total_pedidos": sum(stats_dict.values()),
        "pendentes": stats_dict.get("PENDENTE", 0),
        "aguardando_pagamento": stats_dict.get("AGUARDANDO_PAGAMENTO", 0),
        "pagos": stats_dict.get("PAGO", 0),
        "aceitos": stats_dict.get("ACEITO", 0),
        "concluidos": stats_dict.get("CONCLUIDO", 0),
        "faturamento_total": faturamento
    }


@router.get("/{pedido_id}", response_model=schemas.PedidoOut)
def buscar_por_id(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(models.Pedido).options(
        joinedload(models.Pedido.cliente),
        joinedload(models.Pedido.servico),
        joinedload(models.Pedido.motorista)
    ).filter(models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@router.post("/")
def criar(pedido: schemas.PedidoCreate, db: Session = Depends(get_db)):
    try:
        novo = models.Pedido(**pedido.model_dump())
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{pedido_id}/aceitar")
def aceitar(pedido_id: int, data: schemas.AtribuirMotorista, db: Session = Depends(get_db), current_user: str = Depends(get_usuario_atual)):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id).first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if pedido.motorista_id:
        raise HTTPException(status_code=409, detail="Já aceito")

    motorista = db.query(models.Motorista).filter(
        models.Motorista.id == data.motorista_id).first()

    if not motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    pedido.motorista_id = data.motorista_id
    pedido.status = "ACEITO"

    db.commit()
    db.refresh(pedido)

    return pedido


@router.put("/{pedido_id}/status")
def atualizar_status(pedido_id: int, status_data: schemas.PedidoStatusUpdate, db: Session = Depends(get_db), current_user: str = Depends(get_usuario_atual)):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    pedido.status = status_data.status.upper()
    db.commit()
    db.refresh(pedido)
    return pedido


@router.delete("/{pedido_id}")  # type: ignore
def excluir(pedido_id: int, db: Session = Depends(get_db), current_user: str = Depends(get_usuario_atual)):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    try:
        db.delete(pedido)
        db.commit()
        return {"detail": "Pedido excluído com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
