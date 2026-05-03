from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
import logging
import mercadopago
from backend.database import get_db
from backend import models
from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.routes.whatsapp import broadcast_to_drivers
from backend.config import settings
from backend.services.email_service import enviar_email_transacional

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])
logger = logging.getLogger(__name__)


@router.post("/webhook/mercadopago")
async def webhook_mercadopago(request: Request, db: Session = Depends(get_db)):
    payload = await request.json()
    logger.info(f"Recebendo notificação do Mercado Pago: {payload}")

    # O Mercado Pago envia notificações de diferentes tópicos.
    # Filtramos para processar apenas atualizações de pagamentos.
    resource_type = payload.get("type") or payload.get("topic")
    if resource_type != "payment":
        return {"status": "ignored", "reason": f"Topic {resource_type} is not handled"}

    payment_id = payload.get("data", {}).get("id") or payload.get("id")
    if not payment_id:
        return {"status": "error", "message": "Payment ID not found in payload"}

    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    payment_info = sdk.payment().get(payment_id)
    data = payment_info["response"]

    status_mp = data.get("status")
    order_id = data.get("external_reference")

    if not order_id:
        return {"status": "error", "reason": "no_external_reference"}

    # Garante que o ID seja tratado como inteiro para a busca no banco
    try:
        order_id_int = int(order_id)
    except (ValueError, TypeError):
        return {"status": "error", "message": "Formato de external_reference inválido"}

    pedido = db.query(models.Pedido).filter(
        models.Pedido.id == order_id_int).first()
    if not pedido:
        return {"status": "error", "message": "Pedido não encontrado"}

    if pedido.status != "PAGO":
        pedido.status = "PAGO"
        db.commit()
        db.refresh(pedido)

        _notificar_liberacao(db, pedido)

    return {"status": "ok"}


def _notificar_liberacao(db: Session, pedido: models.Pedido):
    """Helper para disparar notificações após confirmação de pagamento."""
    # 1. Notifica o Cliente
    if pedido.cliente and pedido.cliente.telefone:
        msg_cliente = (
            f"✅ Pagamento confirmado para o pedido #{pedido.id}!\n"
            f"Nossos motoristas já foram notificados e você receberá um aviso assim que o serviço for aceito."
        )
        enviar_whatsapp_meta(pedido.cliente.telefone, msg_cliente)

    # Notifica via E-mail
    if pedido.cliente and pedido.cliente.email:
        assunto = f"✅ Pagamento Confirmado! Pedido #{pedido.id}"
        html = f"<h2>Pagamento Recebido!</h2><p>Olá {pedido.cliente.nome}, recebemos seu pagamento para o serviço <strong>{pedido.servico.nome}</strong>. Em breve enviaremos os dados do motorista.</p>"
        try:
            enviar_email_transacional(pedido.cliente.email, assunto, html)
        except Exception as e:
            logger.error(f"Falha ao enviar e-mail de pagamento: {e}")

    # 2. Notifica os Motoristas
    broadcast_to_drivers(db, pedido)
