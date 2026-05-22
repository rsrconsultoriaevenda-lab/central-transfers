import requests
from backend.config import settings


def enviar_whatsapp_meta(
    numero: str,
    mensagem: str = None,
    payload_interativo: dict = None
):
    token = getattr(settings, "WHATSAPP_TOKEN", None)
    phone_number_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", None)
    api_version = getattr(settings, "WHATSAPP_API_VERSION", "v20.0")

    if not token or not phone_number_id:
        return False, "WhatsApp não configurado"

    url = (
        f"https://graph.facebook.com/"
        f"{api_version}/"
        f"{phone_number_id}/messages"
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    if payload_interativo:
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive": payload_interativo,
        }

    else:
        payload = {
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {
                "body": mensagem
            },
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=15
            )

            response.raise_for_status()

            return True, response.json()

        except requests.exceptions.HTTPError:
            return False, {
                "status_code": response.status_code,
                "erro": response.text
            }

        except requests.exceptions.RequestException as e:
            return False, str(e)
