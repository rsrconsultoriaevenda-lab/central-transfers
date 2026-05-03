from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_usuario_atual

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("/", response_model=List[schemas.PedidoOut])  # type: ignore
def listar_pedidos(
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_usuario_atual)
):
    query = db.query(models.Pedido).options(
        joinedload(models.Pedido.cliente),
        joinedload(models.Pedido.servico),
        joinedload(models.Pedido.motorista)
    )

    if data_inicio:
        query = query.filter(models.Pedido.data_servico >= data_inicio)
    if data_fim:
        query = query.filter(models.Pedido.data_servico <= data_fim)

    return query.order_by(models.Pedido.data_servico.desc()).all()


@router.get("/stats", response_model=schemas.DashboardStats)
def obter_estatisticas(
    data_inicio: Optional[datetime] = Query(None),
    data_fim: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_usuario_atual)
):
    # Filtro base para as estatísticas
    base_query = db.query(models.Pedido)
    if data_inicio:
        base_query = base_query.filter(
            models.Pedido.data_servico >= data_inicio)
    if data_fim:
        base_query = base_query.filter(models.Pedido.data_servico <= data_fim)

    stats = base_query.with_entities(
        models.Pedido.status,
        func.count(models.Pedido.id)
    ).group_by(models.Pedido.status).all()

    stats_dict = {status: count for status, count in stats}

    # Soma do faturamento (apenas pedidos pagos, aceitos ou concluídos)
    faturamento = base_query.with_entities(func.sum(models.Pedido.valor)).filter(
        models.Pedido.status.in_(["PAGO", "ACEITO", "CONCLUIDO"])
    ).scalar() or 0.0

    return {
        "total_pedidos": sum(stats_dict.values()),
        "pendentes": stats_dict.get("PENDENTE", 0),
        "aguardando_pagamento": stats_dict.get("AGUARDANDO_PAGAMENTO", 0),
        "pagos": stats_dict.get("PAGO", 0),
        "aceitos": stats_dict.get("ACEITO", 0),
        "concluidos": stats_dict.get("CONCLUIDO", 0),
        "faturamento_total": faturamento
    }


@router.get("/relatorio/comissoes")
def relatorio_comissoes(db: Session = Depends(get_db), current_user: dict = Depends(get_usuario_atual)):
    # Busca pedidos concluídos agrupados por motorista
    resultados = db.query(
        models.Motorista.nome.label("motorista"),
        func.count(models.Pedido.id).label("total_viagens"),
        func.sum(models.Pedido.valor).label("faturamento_bruto"),
        func.sum(models.Pedido.valor_comissao).label("total_comissao_central")
    ).join(models.Pedido, models.Pedido.motorista_id == models.Motorista.id)\
     .filter(models.Pedido.status == "CONCLUIDO")\
     .group_by(models.Motorista.id).all()

    return [
        {**r._asdict(), "repasse_motorista": float(r.faturamento_bruto or 0) -
         float(r.total_comissao_central or 0)}
        for r in resultados
    ]


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
def criar_pedido(pedido: schemas.PedidoCreate, db: Session = Depends(get_db)):
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
def aceitar(pedido_id: int, data: schemas.AtribuirMotorista, db: Session = Depends(get_db), current_user: dict = Depends(get_usuario_atual)):
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
def atualizar_status_pedido(pedido_id: int, status_data: schemas.PedidoStatusUpdate, db: Session = Depends(get_db), current_user: dict = Depends(get_usuario_atual)):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    pedido.status = status_data.status.upper()
    db.commit()
    db.refresh(pedido)
    return pedido


@router.put("/{pedido_id}/cancelar")
def cancelar(pedido_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_usuario_atual)):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if pedido.status == "CONCLUIDO":
        raise HTTPException(
            status_code=400, detail="Não é possível cancelar um pedido concluído")

    pedido.status = "CANCELADO"
    db.commit()
    db.refresh(pedido)
    return {"detail": f"Pedido {pedido_id} cancelado com sucesso", "status": pedido.status}


@router.delete("/{pedido_id}")  # type: ignore
def excluir(pedido_id: int, db: Session = Depends(get_db), current_user: dict = Depends(get_usuario_atual)):
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
