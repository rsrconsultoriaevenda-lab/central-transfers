from fastapi import APIRouter, Depends, Request, HTTPException, BackgroundTasks, status, Response
from sqlalchemy.orm import Session
import logging
import hashlib
import hmac
from backend.database import get_db
from backend import models
from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.services.notifier_service import notifier
from backend.config import settings
from backend.services.email_service import enviar_email_transacional
from backend.services.payment_service import PaymentService

router = APIRouter(prefix="/pagamentos", tags=["Pagamentos"])
logger = logging.getLogger(__name__)
payment_service = PaymentService()


# ALTERADO: De "/webhook/mercadopago" para "/webhook" para matar o erro 404
@router.post("/webhook")
async def webhook_mercadopago(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Recebe e valida notificações do Mercado Pago com segurança HMAC."""

    # 1. VALIDAÇÃO DE ASSINATURA (HMAC)
    signature_header = request.headers.get("x-signature")
    if not signature_header:
        logger.warning("Tentativa de acesso ao Webhook sem x-signature.")
        return {"status": "ignored"}

    parts = {item.split('=')[0].strip(): item.split('=')[1].strip()
    for item in signature_header.split(',') if '=' in item}
    timestamp = parts.get('ts')
    v1 = parts.get('v1')

    if not timestamp or not v1:
        raise HTTPException(status_code=400, detail="Invalid signature format")

    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    # Verificação do hash com o secret do .env (Garante autenticidade)
    manifest = f"id:{payload.get('data', {}).get('id')};request-id:{request.headers.get('x-request-id')};ts:{timestamp};"
    webhook_secret = getattr(settings, 'MERCADO_PAGO_WEBHOOK_SECRET', "")

    hmac_obj = hmac.new(webhook_secret.encode(), manifest.encode(), hashlib.sha256)
    if not hmac.compare_digest(hmac_obj.hexdigest(), v1):
        logger.error("🚫 Assinatura do Mercado Pago INVÁLIDA!")
        raise HTTPException(status_code=403, detail="Invalid HMAC signature")

    # 2. FILTRAGEM DE EVENTOS
    resource_type = payload.get("type") or payload.get("topic")
    if resource_type != "payment":
        return {"status": "ignored", "reason": f"Topic {resource_type} is not handled"}

    payment_id = payload.get("data", {}).get("id") or payload.get("id")
    if not payment_id:
        raise HTTPException(status_code=400, detail="Payment ID not found in payload")

    # 3. PROCESSAMENTO DA REGRA DE NEGÓCIO (Banco de Dados / Service)
    success = await payment_service.process_payment_update(str(payment_id), db)

    # 4. DISPARO DE NOTIFICAÇÕES SE FOR UM NOVO TRANSFER PAGO
    # Se o pagamento foi processado com sucesso e a referência era de um Pedido, notificamos a rede
    external_ref = payment_service.get_payment_details(str(payment_id))
    if success and external_ref:
        ref_id = external_ref.get("external_reference", "")
        if ref_id.startswith("PEDIDO_") or ref_id.isdigit():
            pedido_id = int(ref_id.replace("PEDIDO_", ""))
            pedido = db.query(models.Pedido).filter(models.Pedido.id == pedido_id).first()
            if pedido:
                # Dispara as notificações pesadas em background para liberar o Mercado Pago rápido
                background_tasks.add_task(_notificar_liberacao, db, pedido, request)

                return {"status": "ok" if success else "processed"}


async def _notificar_liberacao(db: Session, pedido: models.Pedido, request: Request):
    """Helper executado em background para disparar notificações após confirmação."""
    try:
        # 1. Notificação In-App via WebSocket (Painel Administrativo)
        notifier_instance = getattr(request.app.state, "notifier", notifier)
        message_payload = {
            "type": "NEW_ORDER",
            "pedido_id": pedido.id,
            "origem": pedido.origem,
            "destino": pedido.destino,
            "valor": str(pedido.valor),
            "mensagem": f"⚠️ NOVO PEDIDO PAGO: {pedido.origem} → {pedido.destino}"
        }

        if notifier_instance:
            await notifier_instance.broadcast(message_payload)

            # 2. Web Push Notifications (Para os motoristas ativos com PWA instalado)
            motoristas_ativos = db.query(models.Motorista).filter(
                models.Motorista.status == "ATIVO",
                models.Motorista.push_token.isnot(None)
            ).all()

            for m in motoristas_ativos:
                try:
                    await notifier_instance.send_web_push(
                        m.push_token,
                        {
                            "title": "🚖 Novo Pedido Pago!",
                            "body": f"De {pedido.origem} para {pedido.destino}",
                            "url": "/"
                        }
                    )
                except Exception as e:
                    logger.error(f"Falha ao enviar Web Push para motorista {m.id}: {e}")

                    # 3. Notificação via E-mail para o cliente final
                    if pedido.cliente and pedido.cliente.email:
                        assunto = f"✅ Pagamento Confirmado! Pedido #{pedido.id}"
                        html = f"<h2>Pagamento Recebido!</h2><p>Olá {pedido.cliente.nome}, recebemos seu pagamento para o serviço de transfer. Em breve enviaremos os dados do veículo e motorista escalado.</p>"
                        enviar_email_transacional(pedido.cliente.email, assunto, html)

    except Exception as e:
        logger.error(f"Erro no fluxo de background _notificar_liberacao: {e}")