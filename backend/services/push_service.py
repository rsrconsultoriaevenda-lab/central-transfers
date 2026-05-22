import json
from pywebpush import webpush, WebPushException
from backend.config import settings
from backend.database import SessionLocal  # Importar SessionLocal
from backend import models


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
        # Se o token expirou (status 410), tentamos limpar o push_token do motorista.
        if ex.response and ex.response.status_code == 410:
            try:
                endpoint = subscription_info.get("endpoint") if isinstance(
                    subscription_info, dict) else None
                if endpoint:
                    db = SessionLocal()
                    try:
                        motoristas = db.query(models.Motorista).filter(
                            models.Motorista.push_token != None).all()
                        for motorista in motoristas:
                            token = motorista.push_token
                            if isinstance(token, dict) and token.get("endpoint") == endpoint:
                                motorista.push_token = None
                                db.commit()
                                print(
                                    f"Subscription expirada removida de Motorista {motorista.id}")
                                break
                    finally:
                        db.close()
            except Exception as cleanup_err:
                print(f"Falha ao limpar subscription expirada: {cleanup_err}")
            print("Subscription expirada/removida pelo usuário.")
        print(f"Erro no Web Push: {ex}")
        return False
    except Exception as e:
        print(f"Erro genérico no Push: {e}")
        return False
