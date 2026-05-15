import json
from pywebpush import webpush, WebPushException
from backend.config import settings

def send_web_push(subscription_info, data):
    """
    Envia uma notificação push para um dispositivo específico.
    subscription_info: O JSON que o navegador gerou.
    data: Dicionário com title e body.
    """
    try:
        response = webpush(
            subscription_info=subscription_info,
            data=json.dumps(data),
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={"sub": "mailto:admin@centraltransfers.com"}
        )
        return response.ok
    except WebPushException as ex:
        # Se o token expirou (status 410), deveríamos remover do banco
        if ex.response and ex.response.status_code == 410:
            print("Subscription expirada/removida pelo usuário.")
        print(f"Erro no Web Push: {ex}")
        return False
    except Exception as e:
        print(f"Erro genérico no Push: {e}")
        return False
