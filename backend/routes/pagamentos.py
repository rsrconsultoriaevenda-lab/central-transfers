from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging
import mercadopago
import hashlib
import hmac
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
    """Recebe e valida notificações do Mercado Pago com segurança HMAC."""
    # Validação de Assinatura para Produção
    signature_header = request.headers.get("x-signature")
    if not signature_header:
        logger.warning("Tentativa de acesso ao Webhook sem x-signature.")
        return {"status": "ignored"}

    # Extração de parâmetros da assinatura (v1=...,ts=...)
    parts = {item.split('=')[0]: item.split('=')[1]
             for item in signature_header.split(',')}
    timestamp = parts.get('ts')
    v1 = parts.get('v1')

    if not timestamp or not v1:
        raise HTTPException(status_code=400, detail="Invalid signature format")

    payload = await request.json()

    # Verificação de segurança: Validar se o hash bate com o secret do seu .env
    # Isso impede que usuários externos manipulem o status de pagamento
    manifest = f"id:{payload.get('data', {}).get('id')};request-id:{request.headers.get('x-request-id')};ts:{timestamp};"
    hmac_obj = hmac.new(settings.MERCADO_PAGO_WEBHOOK_SECRET.encode(
    ), manifest.encode(), hashlib.sha256)
    if not hmac.compare_digest(hmac_obj.hexdigest(), v1):
        logger.error("🚫 Assinatura do Mercado Pago INVÁLIDA!")
        raise HTTPException(status_code=403, detail="Invalid HMAC signature")

    # Processamento...
    if payload.get("action") != "payment.created" and payload.get("type") != "payment":
        return {"status": "ignored"}

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
    external_reference = data.get("external_reference")

    if not external_reference or status_mp != "approved":
        return {"status": "error", "reason": "no_external_reference"}

    if external_reference.startswith("MENSAL_"):
        mensalidade_id = int(external_reference.replace("MENSAL_", ""))
        mensalidade = db.query(models.Mensalidade).filter(
            models.Mensalidade.id == mensalidade_id).with_for_update().first()

        if mensalidade and mensalidade.status != "PAGO":
            mensalidade.status = "PAGO"
            mensalidade.data_pagamento = datetime.now()

            # REGRA DE NEGÓCIO: Reativar motorista se estiver bloqueado por falta de pagamento
            motorista = mensalidade.motorista
            if motorista and motorista.status == "TRIAL_EXPIRADO":
                motorista.status = "ATIVO"
                logger.info(
                    f"Motorista {motorista.id} reativado após pagamento da mensalidade.")
                enviar_whatsapp_meta(
                    motorista.telefone, f"✅ Pagamento confirmado! Sua conta foi reativada. Bom trabalho!")

            db.commit()
            logger.info(f"Mensalidade {mensalidade_id} marcada como PAGA.")
        return {"status": "ok"}

    elif external_reference.startswith("PEDIDO_") or external_reference.isdigit():
        # Suporte ao formato antigo (apenas dígitos) e ao novo (PEDIDO_ID)
        order_id_raw = external_reference.replace("PEDIDO_", "")
        order_id_int = int(order_id_raw)

        pedido = db.query(models.Pedido).filter(
            models.Pedido.id == order_id_int).first()
        if not pedido:
            return {"status": "error", "message": "Pedido não encontrado"}

        if pedido.status != "PAGO":
            pedido.status = "PAGO"
            db.commit()
            db.refresh(pedido)
            await _notificar_liberacao(db, pedido, request)

    return {"status": "ok", "message": "Webhook processed successfully"}


async def _notificar_liberacao(db: Session, pedido: models.Pedido, request: Request):
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
    # Tenta WhatsApp (se configurado)
    try:
        broadcast_to_drivers(db, pedido)
    except:
        pass

    # Notificação In-App (Estilo Uber)
    # Acessamos o manager do app para disparar o WebSocket
    import asyncio
    notifier = getattr(request.app.state, "notifier", None)
    if notifier:
        asyncio.create_task(notifier.notify_drivers({
            "type": "NEW_ORDER",
            "pedido_id": pedido.id,
            "mensagem": f"Novo pedido disponível: {pedido.origem} para {pedido.destino}",
            "valor": str(pedido.valor)
        }))
