import hmac
import hashlib
import json
import requests
import time

# AJUSTE ESTAS VARIÁVEIS CONFORME SEU .ENV LOCAL
# Se você usou o setup_env.py, as chaves foram geradas lá.
BASE_URL = "http://127.0.0.1:8001/whatsapp/incoming"
# Verifique no seu .env (WHATSAPP_APP_SECRET)
APP_SECRET = "sua_chave_app_secret_real_aqui"
# Verifique no seu .env (WHATSAPP_VERIFY_TOKEN)
VERIFY_TOKEN = "seu_verify_token_real_aqui"


def test_meta_handshake():
    print("\n[1] Testando Verificação de Token (GET)...")
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": VERIFY_TOKEN,
        "hub.challenge": "CHALLENGE_ACCEPTED"
    }
    try:
        r = requests.get(BASE_URL, params=params)
        if r.status_code == 200 and r.text == "CHALLENGE_ACCEPTED":
            print("✅ Handshake de verificação: OK")
        else:
            print(f"❌ Falha no Handshake: {r.status_code} - {r.text}")
    except Exception as e:
        print(f"💥 Erro de conexão: {e}")


def test_meta_message_flow():
    print("\n[2] Testando Fluxo de Mensagem com Assinatura (POST)...")

    # Payload no formato exato da Cloud API da Meta
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "5554999999999", "phone_number_id": "12345"},
                    "contacts": [{"profile": {"name": "Cliente Teste"}, "wa_id": "5554988887777"}],
                    "messages": [{
                        "from": "5554988887777",
                        "id": "wamid.ID_TESTE",
                        "timestamp": str(int(time.time())),
                        "text": {"body": "Pedido transfer origem: Hotel destino: Aeroporto data: 25/05 10:00 valor: 150"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }

    body = json.dumps(payload, separators=(',', ':')).encode('utf-8')

    # Gerando a assinatura SHA256 que a Meta enviaria
    signature = hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": f"sha256={signature}"
    }

    r = requests.post(BASE_URL, data=body, headers=headers)
    print(f"Status Code: {r.status_code}")
    try:
        print(f"Resposta do Servidor: {r.json()}")
    except:
        print(f"Resposta do Servidor (Texto): {r.text}")

    print("ℹ️ Verifique os logs do seu backend para ver o processamento em background.")


if __name__ == "__main__":
    test_meta_handshake()
    test_meta_message_flow()
