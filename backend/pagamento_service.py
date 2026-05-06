import mercadopago
from backend.config import settings

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