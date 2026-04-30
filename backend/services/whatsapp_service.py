import requests
import json
from backend.config import settings


def enviar_whatsapp_meta(numero: str, mensagem: str, payload_interativo: dict = None):
    token = settings.WHATSAPP_TOKEN
    phone_number_id = settings.WHATSAPP_PHONE_NUMBER_ID
    api_version = settings.WHATSAPP_API_VERSION

    if not token or not phone_number_id:
        return None, "WhatsApp não configurado"

    base_url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    if payload_interativo:
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive": payload_interativo
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {
                "body": mensagem
            }
        }

    response = requests.post(
        base_url,
        headers=headers,
        data=json.dumps(payload)
    )

    return response.status_code, response.text
