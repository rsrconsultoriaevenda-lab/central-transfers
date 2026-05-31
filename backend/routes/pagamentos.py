from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks, status
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging
import hmac
import hashlib
from backend.database import get_db
from backend import models
from backend.auth import get_usuario_atual
from backend.pagamento_service import criar_checkout_pro, process_payment_update, get_payment_details
from backend.services.notifier_service import notifier
from backend.config import settings

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])
logger = logging.getLogger(__name__)


@router.post("/checkout/")
@router.post("/checkout")
async def gerar_checkout(request: Request, db: Session = Depends(get_db)):
    """Processa o checkout criando o pedido a partir do carrinho e metadados."""
    try:
        data = await request.json()
    except Exception:
        raise HTTPException(
            status_code=400, detail="Corpo da requisição inválido")

    pedido_id = data.get("pedido_id")
    itens = data.get("itens", [])
    meta = data.get("metadata", {})

    # Se não existe pedido_id, criamos o pedido via carrinho e metadados
    if not pedido_id and itens:
        tel = meta.get("telefone", "00000000000")
        cliente = db.query(models.Cliente).filter(
            models.Cliente.telefone == tel).first()
        if not cliente:
            cliente = models.Cliente(nome=meta.get(
                "nome", "Cliente Site"), telefone=tel)
            db.add(cliente)
            db.flush()  # Obtém o ID sem encerrar a transação atual

        # Conversão segura de data: O banco de dados exige um objeto datetime
        data_raw = meta.get("data")
        try:
            if data_raw and isinstance(data_raw, str):
                data_servico = datetime.fromisoformat(
                    data_raw.replace("Z", "+00:00"))
            else:
                data_servico = datetime.now(timezone.utc).replace(tzinfo=None)
        except (ValueError, TypeError):
            data_servico = datetime.now(timezone.utc).replace(tzinfo=None)

        novo_pedido = models.Pedido(
            cliente_id=cliente.id,
            servico_id=itens[0].get("id") if itens else None,
            origem=meta.get("origem", "A definir"),
            destino=meta.get("destino", "A definir"),
            data_servico=data_servico,
            valor=float(round(sum(Decimal(str(i.get("preco") or 0)) *
                                  i.get("quantidade", 1) for i in itens), 2)),
            observacoes=meta.get("observacoes", ""),
            status="PENDENTE"
        )
        novo_pedido.calcular_financeiro()
        db.add(novo_pedido)
        db.commit()
        db.refresh(novo_pedido)
        pedido_id = novo_pedido.id

    # Processa o pedido (seja o recém-criado ou o ID recebido)
    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == pedido_id).first()
    if not pedido:
        raise HTTPException(status_code=404, detail="Pedido não encontrado")

    try:
        checkout_url = criar_checkout_pro(
            item_id=f"PEDIDO_{pedido.id}",
            valor=round(float(pedido.valor), 2) if pedido.valor else 0.0,
            descricao=f"Transfer: {pedido.origem} -> {pedido.destino}",
            item_type="PEDIDO",
            payer_email=meta.get("email"),
            payer_cpf=meta.get("cpf")
        )
        return {"init_point": checkout_url}
    except Exception as e:
        logger.error(f"Erro ao gerar checkout MP: {e}")
        raise HTTPException(
            status_code=500, detail="Falha ao gerar link de pagamento")


@router.post("/webhook")
async def webhook_mercadopago(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Recebe notificação, processa pagamento e dispara notificações."""
    payload = await request.json()
        
    # Recomendação: Validar X-Signature do Mercado Pago aqui
    # Para o MVP, validamos ao menos se o evento é de pagamento
    action = payload.get("action")
    if action not in ["payment.created", "payment.updated"]:
        return {"status": "ignored", "reason": "action_not_supported"}

    data_obj = payload.get("data")
    if not data_obj or not data_obj.get("id"):
        logger.info(f"Webhook ignorado: payload sem ID de dados ({payload.get('action')})")
        return {"status": "ignored"}

    payment_id = data_obj.get("id")

    success = await process_payment_update(str(payment_id), db)
    if success:
        payment_data = get_payment_details(str(payment_id))
        ref_id = str(payment_data.get("external_reference", "")
                     ).replace("PEDIDO_", "")
        pedido = db.query(models.Pedido).filter(
            models.Pedido.id == int(ref_id)).first()
        if pedido:
            background_tasks.add_task(_notificar_liberacao, db, pedido)
            return {"status": "ok"}


@router.get("/stats")
async def get_driver_stats(
    period: str = "semanal", 
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    """Retorna estatísticas financeiras reais para o motorista."""
    if user.get("role") != "motorista":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acesso restrito a motoristas"
        )

    email = user.get("email")
    motorista = db.query(models.Motorista).filter(models.Motorista.email == email).first()
    
    if not motorista:
        raise HTTPException(status_code=404, detail="Perfil de motorista não encontrado")

    motorista_id = motorista.id

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if period == "semanal":
        start_date = now - timedelta(days=7)
    elif period == "mensal":
        start_date = now - timedelta(days=30)
    else:  # anual
        start_date = now - timedelta(days=365)

    # Agregações via Banco de Dados para performance
    stats = db.query(
        func.sum(models.Pedido.valor_liquido_motorista).label("faturamento"),
        func.count(models.Pedido.id).label("total")
    ).filter(
        models.Pedido.motorista_id == motorista_id,
        models.Pedido.status == "CONCLUIDO",
        models.Pedido.data_servico >= start_date
    ).first()

    # Lista detalhada para o histórico
    pedidos = db.query(models.Pedido).filter(
        models.Pedido.motorista_id == motorista_id,
        models.Pedido.status == "CONCLUIDO",
        models.Pedido.data_servico >= start_date
    ).order_by(models.Pedido.data_servico.desc()).all()

    lista_formatada = [
        {
            "id": p.id,
            "data": p.data_servico.strftime("%d %b"),
            "rota": f"{p.origem} ➔ {p.destino}",
            "valor": float(p.valor or 0),
            "status": "CONCLUÍDO"
        } for p in pedidos
    ]
    
    total_faturamento = stats.faturamento or Decimal("0.00")

    return {
        "faturamento": f"R$ {total_faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
        "corridas": stats.total or 0,
        # Mock de KM baseado na média de corridas na região
        "km": f"{(stats.total or 0) * 45} km",
        "lista": lista_formatada
    }


async def _notificar_liberacao(db: Session, pedido: models.Pedido):
    """Dispara alerta em tempo real para o DriverApp."""
    message = {
        "type": "NEW_ORDER",
        "pedido_id": pedido.id,
        "mensagem": f"Novo pedido: {pedido.origem} -> {pedido.destino}",
        "origem": pedido.origem,
        "destino": pedido.destino,
        "valor": float(pedido.valor) if pedido.valor else 0.0
    }
    await notifier.broadcast(message)
