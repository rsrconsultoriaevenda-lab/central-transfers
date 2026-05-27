import mercadopago
from backend.config import settings
from backend import models
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from decimal import Decimal


def get_payment_details(payment_id: str):
    """Consulta os detalhes de um pagamento na API do Mercado Pago."""
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)
    payment_info = sdk.payment().get(payment_id)
    return payment_info.get("response", {})


async def process_payment_update(payment_id: str, db: Session):
    """
    Busca detalhes do pagamento e atualiza o status do Pedido ou Mensalidade.
    """
    payment_data = get_payment_details(payment_id)
    status = payment_data.get("status")
    external_reference = payment_data.get("external_reference")

    if not external_reference or status != "approved":
        return False

    try:
        if external_reference.startswith("PEDIDO_"):
            pedido_id = int(external_reference.replace("PEDIDO_", ""))
            pedido = db.query(models.Pedido).filter(
                models.Pedido.id == pedido_id).first()

            if pedido and pedido.status != models.StatusPedido.PAGO:
                pedido.status = models.StatusPedido.PAGO
                pedido.calcular_financeiro()
                db.commit()
                return True

        elif external_reference.startswith("MENSAL_"):
            mensal_id = int(external_reference.replace("MENSAL_", ""))
            mensalidade = db.query(models.Mensalidade).filter(
                models.Mensalidade.id == mensal_id).first()

            if mensalidade and mensalidade.status != "PAGO":
                mensalidade.status = "PAGO"
                mensalidade.data_pagamento = datetime.now(timezone.utc)

                # Também atualiza o motorista
                if mensalidade.motorista:
                    mensalidade.motorista.status = "ATIVO"
                    mensalidade.motorista.mensalidade_ativa = True

                db.commit()
                return True
    except Exception as e:
        print(f"Erro ao processar webhook: {e}")
        db.rollback()

    return False


def criar_checkout_pro(item_id: int, valor: float, descricao: str, item_type: str = "PEDIDO"):
    """
    Cria uma preferência de pagamento no Mercado Pago.
    item_type pode ser 'PEDIDO' ou 'MENSAL'.
    """
    sdk = mercadopago.SDK(settings.MERCADO_PAGO_ACCESS_TOKEN)

    # Utilizamos um prefixo no external_reference para o webhook saber o que processar
    external_ref = f"{item_type}_{item_id}"

    preference_data = {
        "items": [
            {
                "title": descricao,
                "quantity": 1,
                "unit_price": float(valor),
            }
        ],
        "external_reference": external_ref,
        "back_urls": {
            "success": f"{settings.FRONTEND_URL}/success",
            "pending": f"{settings.FRONTEND_URL}/pending",
            "failure": f"{settings.FRONTEND_URL}/failure",
        },
        "auto_return": "approved",
    }

    preference_response = sdk.preference().create(preference_data)
    return preference_response["response"]["init_point"]
