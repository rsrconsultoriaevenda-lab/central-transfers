from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
import requests
import logging
from backend.database import get_db
from backend import models
from backend.config import settings
from backend.routes.whatsapp import broadcast_to_drivers

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])
logger = logging.getLogger(__name__)


@router.post("/mercadopago")
async def webhook_mercadopago(request: Request, db: Session = Depends(get_db)):
    """
    Endpoint que recebe notificações do Mercado Pago.
    Configurar esta URL no painel do MP: https://seu-dominio.com/webhooks/mercadopago
    """
    try:
        payload = await request.json()

        # Verificamos se a notificação é de um pagamento
        if payload.get("type") == "payment":
            payment_id = payload.get("data", {}).get("id")

            if not payment_id:
                return {"status": "ignored"}

            # Consultamos os detalhes reais do pagamento diretamente na API do MP por segurança
            # Usando o token de config
            headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}
            # Nota: Idealmente use um token específico MERCADOPAGO_TOKEN no seu .env

            mp_res = requests.get(
                f"https://api.mercadopago.com/v1/payments/{payment_id}",
                headers=headers
            )

            if mp_res.status_code == 200:
                payment_info = mp_res.json()
                status = payment_info.get("status")
                # O 'external_reference' deve ter sido configurado como o ID do pedido na criação do checkout
                pedido_id = payment_info.get("external_reference")

                if status == "approved" and pedido_id:
                    pedido = db.query(models.Pedido).filter(
                        models.Pedido.id == int(pedido_id)).first()

                    if pedido and pedido.status != "PAGO":
                        pedido.status = "PAGO"
                        db.commit()

                        # Dispara automaticamente o bipe para todos os motoristas
                        broadcast_to_drivers(db, pedido)
                        logger.info(
                            f"✅ Pedido {pedido_id} confirmado via Webhook.")

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"❌ Erro no Webhook: {e}")
        return {"status": "error", "detail": str(e)}
