import os
import requests
import json
from pathlib import Path


def _load_env_file():
    redis_project_root = Path(__file__).resolve().parents[2]
    env_paths = [
        redis_project_root / ".env",
        redis_project_root / "backend" / ".env",
    ]

    for path in env_paths:
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    os.environ.setdefault(key.strip(), value.strip())


_load_env_file()


def enviar_whatsapp_meta(numero: str, mensagem: str):
    token = os.getenv("WHATSAPP_TOKEN")
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    api_version = os.getenv("WHATSAPP_API_VERSION", "v20.0")

    if not token or not phone_number_id:
        return None, "WhatsApp não configurado"

    base_url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

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