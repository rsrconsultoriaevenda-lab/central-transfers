import asyncio

from datetime import datetime
from decimal import Decimal
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend import models, schemas
from backend.auth import get_usuario_atual
from backend.database import get_db

router = APIRouter(
    prefix="/pedidos",
    tags=["Pedidos"]
)

# =====================================================
# TESTE DE CONECTIVIDADE REAL-TIME
# =====================================================
@router.get("/debug-broadcast")
async def test_realtime_broadcast(request: Request):
    """Envia um sinal de teste para todos os motoristas conectados no PWA."""
    notifier = getattr(request.app.state, "notifier", None)
    if not notifier:
        return {"status": "error", "message": "Serviço de notificação não inicializado"}
    
    await notifier.broadcast({
        "type": "SYSTEM_TEST",
        "mensagem": "🔔 Teste de conexão em tempo real: OK!",
        "valor": "0.00",
        "pedido_id": 0,
        "origem": "Sistema",
        "destino": "Todos"
    })
    return {"status": "sent", "active_connections": len(notifier.active_connections)}


# =====================================================
# LISTAR PEDIDOS
# =====================================================
@router.get("/", response_model=List[schemas.PedidoOut])
def listar_pedidos(
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    query = db.query(models.Pedido)

    # Filtro por Role: Motoristas só vêem seus pedidos ou pedidos disponíveis (PENDENTE/PAGO)
    if user.get("role") == "motorista":
        # Aqui você pode customizar: motoristas vêem pedidos sem dono ou os seus próprios
        # Para este exemplo, limitaremos aos pedidos dele ou abertos.
        from sqlalchemy import or_
        email = user.get("email")
        motorista = db.query(models.Motorista).filter(
            models.Motorista.email == email).first()
        motorista_id = motorista.id if motorista else None

        query = query.filter(
            or_(models.Pedido.motorista_id == motorista_id, models.Pedido.status == "PAGO"))

    return query.order_by(models.Pedido.criado_at.desc()).all()


# =====================================================
# CRIAR PEDIDO
# =====================================================
@router.post(
    "/",
    response_model=schemas.PedidoOut,
    status_code=status.HTTP_201_CREATED
)
def criar_pedido(
    pedido_in: schemas.PedidoCreate,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual)
):
    servico = db.query(models.Servico).filter(
        models.Servico.id == pedido_in.servico_id
    ).first()

    if not servico:
        raise HTTPException(
            status_code=404,
            detail="Serviço não encontrado"
        )

    novo_pedido = models.Pedido(
        **pedido_in.model_dump(),
        servico=servico
    )

    novo_pedido.calcular_financeiro()

    db.add(novo_pedido)
    db.commit()
    db.refresh(novo_pedido)

    return novo_pedido

# =====================================================
# ATUALIZAR STATUS
# =====================================================


@router.put("/{pedido_id}/status", response_model=schemas.PedidoOut)
async def atualizar_status(
    pedido_id: int,
    status_update: schemas.PedidoStatusUpdate,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual)
):
    # SEGURANÇA: Apenas admin ou operador pode mudar o status manualmente
    if usuario.get("role") not in ["admin", "operador"]:
        raise HTTPException(
            status_code=403, detail="Acesso negado para alteração manual de status")

    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    pedido.status = status_update.status

    # Recalcula financeiro
    pedido.calcular_financeiro()

    db.commit()

    # Notificação WebSocket: Se o pagamento foi aprovado, avisar motoristas
    if pedido.status == "PAGO":
        notifier = getattr(request.app.state, "notifier", None)
        if notifier:
            try:
                asyncio.create_task(
                    notifier.broadcast({
                        "type": "NEW_ORDER",
                        "pedido_id": pedido.id,
                        "origem": pedido.origem,
                        "destino": pedido.destino,
                        "valor": str(pedido.valor),
                        "mensagem": f"Novo pedido: {pedido.origem} para {pedido.destino}"
                    })
                )
            except Exception as e:
                print(f"⚠️ Falha ao disparar notificação WebSocket: {e}")

    db.refresh(pedido)

    return pedido

# =====================================================
# ACEITAR PEDIDO
# =====================================================


@router.put("/{pedido_id}/aceitar", response_model=schemas.PedidoOut)
async def atribuir_motorista(
    pedido_id: int,
    data: schemas.AtribuirMotorista,
    request: Request,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual)
):
    # SEGURANÇA: Se o usuário for motorista, ele só pode aceitar para o próprio ID
    if usuario.get("role") == "motorista":
        email = usuario.get("email")
        motorista_vinculado = db.query(models.Motorista).filter(
            models.Motorista.email == email).first()

        if not motorista_vinculado or motorista_vinculado.id != data.motorista_id:
            raise HTTPException(
                status_code=403,
                detail="Você não tem permissão para atribuir pedidos a outros motoristas."
            )

    query = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    )

    # Lock somente em bancos compatíveis
    if db.bind.name != "sqlite":
        query = query.with_for_update()

    pedido = query.first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    if pedido.motorista_id is not None:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Este pedido já foi aceito por outro motorista."
        )

    motorista = db.query(models.Motorista).filter(
        models.Motorista.id == data.motorista_id
    ).first()

    if not motorista:
        raise HTTPException(
            status_code=404,
            detail="Motorista não encontrado"
        )

    # Validação de plano mensal
    if motorista.plano == "MENSAL":
        inicio_mes = datetime.now().replace(
            day=1,
            hour=0,
            minute=0,
            second=0,
            microsecond=0
        )

        contagem_mes = db.query(models.Pedido).filter(
            models.Pedido.motorista_id == motorista.id,
            models.Pedido.status.in_(["ACEITO", "CONCLUIDO"]),
            models.Pedido.data_servico >= inicio_mes
        ).count()

        if contagem_mes >= 5:
            db.rollback()
            raise HTTPException(
                status_code=400,
                detail=(
                    "Limite de 5 serviços mensais atingido "
                    "no plano Standard."
                )
            )

    pedido.motorista = motorista
    pedido.status = "ACEITO"

    # Recalcula financeiro
    pedido.calcular_financeiro()

    db.commit()

    # Notificação websocket
    notifier = getattr(request.app.state, "notifier", None)

    if notifier:
        asyncio.create_task(
            notifier.broadcast({
                "type": "ORDER_ACCEPTED",
                "pedido_id": pedido.id,
                "mensagem": f"O pedido #{pedido.id} foi aceito por outro motorista."
            })
        )

    db.refresh(pedido)
    return pedido

# =====================================================
# DASHBOARD STATS
# =====================================================


@router.get("/stats", response_model=schemas.DashboardStats)
def obter_estatisticas(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual)
):

    query = db.query(models.Pedido)
    total = query.count()
    pendentes = query.filter(
        models.Pedido.status == "PENDENTE"
    ).count()
    aguardando = query.filter(
        models.Pedido.status == "AGUARDANDO_PAGAMENTO"
    ).count()
    pagos = query.filter(
        models.Pedido.status == "PAGO"
    ).count()
    aceitos = query.filter(
        models.Pedido.status == "ACEITO"
    ).count()
    concluidos = query.filter(
        models.Pedido.status == "CONCLUIDO"
    ).count()
    faturamento = db.query(
        func.sum(models.Pedido.valor)
    ).filter(
        models.Pedido.status == "CONCLUIDO"
    ).scalar() or Decimal("0.00")  # Garante Decimal

    return schemas.DashboardStats(
        total_pedidos=total,
        pendentes=pendentes,
        aguardando_pagamento=aguardando,
        pagos=pagos,
        aceitos=aceitos,
        concluidos=concluidos,
        faturamento_total=faturamento
    )

# =====================================================
# OBTER PEDIDO
# =====================================================


@router.get("/{pedido_id}", response_model=schemas.PedidoOut)
def obter_pedido(
    pedido_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual)
):

    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id
    ).first()

    if not pedido:
        raise HTTPException(
            status_code=404,
            detail="Pedido não encontrado"
        )

    return pedido
