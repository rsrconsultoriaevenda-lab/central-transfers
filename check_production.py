import requests
import sys


def check_api(url):
    print(f"--- Verificando Saúde da API: {url} ---")
    try:
        # 1. Verifica Endpoint Raiz
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"[OK] API Online. Database: {data.get('database')}")
            print(f"[OK] Ambiente: {data.get('environment')}")
        else:
            print(f"[ERRO] API retornou status {resp.status_code}")

        # 2. Verifica Webhook Handshake
        # Simula a verificação da Meta
        webhook_url = f"{url}/whatsapp/incoming"
        params = {
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge",
            "hub.verify_token": "meu_token_secreto_123"  # Altere se mudou no .env
        }
        resp_web = requests.get(webhook_url, params=params, timeout=10)
        if resp_web.status_code == 200 and resp_web.text == "test_challenge":
            print("[OK] Webhook configurado e pronto para a Meta API.")
        else:
            print("[AVISO] Webhook não validou. Verifique o WHATSAPP_VERIFY_TOKEN.")

    except Exception as e:
        print(f"[FALHA CRÍTICA] Não foi possível conectar: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python check_production.py https://seu-app.onrender.com")
    else:
        target_url = sys.argv[1].rstrip('/')
        check_api(target_url)
