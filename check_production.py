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
                f"✅ [OK] API Online. Status do Banco: {data.get('database') or 'Operacional'}")
            print(f"[OK] Ambiente: {data.get('environment')}")
            print(f"[OK] Status Geral: Sistema pronto para uso.")
        else:
            print(
                f"❌ [ERRO] API ({health_url}) retornou status {resp.status_code}")
            print(
                f"👉 Dica: O erro 502 no Railway significa que o container deu 'crash' no boot.\n"
                f"   1. Verifique se a DATABASE_URL no Railway começa com 'postgresql://' (adicione o 'ql' se faltar).\n"
                f"   2. Certifique-se de que a variável DATABASE_URL termina com '?sslmode=require'.\n"
                f"   3. Execute 'railway logs' no terminal ou veja a aba 'Logs' no painel web.\n"
                f"   2. Veja a aba 'Logs' no Railway para o erro real (ex: Connection Refused).")

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
        print("Uso: python check_production.py https://central-transfers-production.up.railway.app")
    else:
        target_url = sys.argv[1].rstrip('/')
        check_api(target_url)
