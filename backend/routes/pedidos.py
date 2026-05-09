import asyncio
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from backend import models, schemas
from backend.database import get_db
from backend.auth import get_usuario_atual
from decimal import Decimal

router = APIRouter(prefix="/pedidos", tags=["Pedidos"])


@router.get("/", response_model=List[schemas.PedidoOut])
def listar_pedidos(db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    return db.query(models.Pedido).order_by(models.Pedido.criado_at.desc()).all()


@router.post("/", response_model=schemas.PedidoOut, status_code=status.HTTP_201_CREATED)
def criar_pedido(pedido_in: schemas.PedidoCreate, db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    novo_pedido = models.Pedido(**pedido_in.model_dump())

    # O cálculo financeiro inicial acontece antes de salvar no banco
    novo_pedido.calcular_financeiro()

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)
    return novo_pedido


@router.get("/{pedido_id}", response_model=schemas.PedidoOut)
def obter_pedido(pedido_id: int, db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")
    return pedido


@router.put("/{pedido_id}/status", response_model=schemas.PedidoOut)
def atualizar_status(pedido_id: int, status_update: schemas.PedidoStatusUpdate, db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    # Garante que ao mudar para CONCLUIDO ou PAGO, o financeiro esteja atualizado
    pedido.calcular_financeiro()

    pedido.status = status_update.status
    db.commit()
    db.refresh(pedido)
    return pedido


@router.put("/{pedido_id}/aceitar", response_model=schemas.PedidoOut)
async def atribuir_motorista(pedido_id: int, data: schemas.AtribuirMotorista, request: Request, db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    # Usa with_for_update() para bloquear a linha do banco e evitar que outro motorista aceite simultaneamente
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id).with_for_update().first()

    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    if pedido.motorista_id is not None:
        db.rollback()
        raise HTTPException(
            status_code=400, detail="Este pedido já foi aceito por outro motorista.")

    motorista = db.query(models.Motorista).filter(
        models.Motorista.id == data.motorista_id).first()
    if not motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    # Validação de Limite para Plano Standard (MENSAL)
    if motorista.plano == "MENSAL":
        inicio_mes = datetime.now().replace(
            day=1, hour=0, minute=0, second=0, microsecond=0)
        contagem_mes = db.query(models.Pedido).filter(
            models.Pedido.motorista_id == motorista.id,
            models.Pedido.status.in_(["ACEITO", "CONCLUIDO"]),
            models.Pedido.data_servico >= inicio_mes
        ).count()

        if contagem_mes >= 5:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail="Limite de 5 serviços mensais atingido no plano Standard. Migre para o plano Master para serviços ilimitados."
            )

    # Associa o motorista e muda status
    pedido.motorista = motorista
    pedido.status = "ACEITO"

    # Recalcula automaticamente o financeiro (Líquido do Motorista) baseado no plano dele
    pedido.calcular_financeiro()

    db.commit()

    # Notifica via WebSocket que o pedido foi aceito
    notifier = request.app.state.notifier
    asyncio.create_task(notifier.notify_drivers({
        "type": "ORDER_ACCEPTED",
        "pedido_id": pedido.id
    }))

    db.refresh(pedido)
    return pedido


@router.get("/stats", response_model=schemas.DashboardStats)
def obter_estatisticas(db: Session = Depends(get_db), usuario=Depends(get_usuario_atual)):
    # Agregando estatísticas para o Dashboard Administrativo
    query = db.query(models.Pedido)

    total = query.count()
    pendentes = query.filter(models.Pedido.status == "PENDENTE").count()
    aguardando = query.filter(models.Pedido.status ==
                              "AGUARDANDO_PAGAMENTO").count()
    pagos = query.filter(models.Pedido.status == "PAGO").count()
    aceitos = query.filter(models.Pedido.status == "ACEITO").count()
    concluidos = query.filter(models.Pedido.status == "CONCLUIDO").count()

    faturamento = db.query(func.sum(models.Pedido.valor)).filter(
        models.Pedido.status == "CONCLUIDO"
    ).scalar() or 0.0

    return schemas.DashboardStats(
        total_pedidos=total,
        pendentes=pendentes,
        aguardando_pagamento=aguardando,
        pagos=pagos,
        aceitos=aceitos,
        concluidos=concluidos,
        faturamento_total=Decimal(str(faturamento))
    )
