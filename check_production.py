import requests
import sys


def check_api(url):
    print(f"--- Verificando Saúde da API: {url} ---")
    try:
        # 1. Verifica Endpoint de Saúde
        health_url = f"{url}/health"
        resp = requests.get(health_url, timeout=10)

        if resp.status_code == 200:
            data = resp.json()
            print(
                f"[OK] API Online. Database: {data.get('database') or 'Conectado'}")
            print(f"[OK] Ambiente: {data.get('environment')}")
            print(f"[OK] Status Geral: Sistema pronto para uso.")
        else:
            print(
                f"❌ [ERRO] API ({health_url}) retornou status {resp.status_code}")
            print(
                f"👉 Dica: O erro 502 Bad Gateway no Railway geralmente significa que a aplicação deu 'crash' no boot.\n"
                f"   Verifique os Logs no painel do Railway para ver o erro do Python/Alembic.")

        print(f"\n--- Verificando Webhook (Opcional) ---")
        webhook_url = f"{url}/whatsapp/incoming"
        params = {
            "hub.mode": "subscribe",
            "hub.challenge": "test_challenge",
            "hub.verify_token": "validacao_apenas"
        }
        try:
            resp_web = requests.get(webhook_url, params=params, timeout=5)
            if resp_web.status_code == 502:
                print(
                    "⚠️ [AVISO] Webhook também retornou 502 (Container offline).")
            else:
                print(
                    f"[INFO] Resposta do Webhook: HTTP {resp_web.status_code}")
        except:
            print("[INFO] Webhook não respondeu (timeout).")

    except Exception as e:
        print(f"[FALHA CRÍTICA] Não foi possível conectar: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python check_production.py https://seu-app.onrender.com")
    else:
        target_url = sys.argv[1].rstrip('/')
        check_api(target_url)
