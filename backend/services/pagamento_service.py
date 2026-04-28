import mercadopago
from backend.config import settings
import logging

logger = logging.getLogger(__name__)


def criar_checkout_pro(pedido_id: int, valor: float):
    """Cria uma preferência de pagamento no Checkout Pro do Mercado Pago."""
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    preference_data = {
        "items": [
            {
                "title": f"Pedido #{pedido_id}",
                "quantity": 1,
                "unit_price": float(valor),
                "currency_id": "BRL"
            }
        ],
        "external_reference": str(pedido_id),
        "back_urls": {
            "success": "https://central-transfers-admin.vercel.app/success",
            "failure": "https://central-transfers-admin.vercel.app/failure",
            "pending": "https://central-transfers-admin.vercel.app/pending"
        },
        "auto_return": "approved"
    }

    try:
        response = sdk.preference().create(preference_data)
    except Exception as e:
        logger.error(f"Falha na comunicação com Mercado Pago: {e}")
        raise Exception("Serviço de pagamento indisponível")

    # Acesso seguro ao init_point
    result = response.get("response")
    if result and "init_point" in result:
        return result["init_point"]

    logger.error(f"❌ Erro ao gerar preferência no Mercado Pago: {response}")
    raise Exception(
        "Falha ao gerar link de pagamento. Verifique o token do Mercado Pago.")


def consultar_status_pagamento(payment_id: str):
    """Consulta o status real de um pagamento no Mercado Pago."""
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    try:
        payment_info = sdk.payment().get(payment_id)
        return payment_info["response"]
    except Exception as e:
        logger.error(f"Erro ao consultar pagamento {payment_id}: {e}")
        return None
