import sys
import requests

# 1. DEFINIÇÃO DA URL BASE
url = "https://central-transfers-production.up.railway.app"
if len(sys.argv) > 1:
    url = sys.argv[1].rstrip('/')

    # 2. DEFINIÇÃO DAS ROTAS (Corrigido: Fora do bloco 'if', alinhado à esquerda)
    health_url = f"{url}/health"
    webhook_url = f"{url}/pagamentos/webhook"


print("\n--- 1. Iniciando Validação do Ambiente de Produção ---")
print(f"[INFO] Testando rota principal: {health_url}")

try:
    resp = requests.get(health_url, timeout=5)
    if resp.status_code == 200:
        print(f"[OK] Status Geral: Sistema pronto para uso (HTTP 200).")
    else:
        print(
            f"❌ [ERRO] API ({health_url}) retornou status {resp.status_code}")
        print("   👉 Dica: Verifique os logs no painel do Railway.")
except requests.exceptions.RequestException as e:
    print(f"❌ [ERRO] Não foi possível conectar à API principal: {e}")


print("\n--- 2. Verificando Webhook Mercado Pago ---")
print(f"[INFO] Testando endpoint: {webhook_url}")

# Payload idêntico ao que o Mercado Pago envia
payload_teste = {
    "action": "payment.updated",
    "api_version": "v1",
    "data": {"id": "123456"},
    "date_created": "2026-05-25T20:00:00Z",
    "id": "123456",
    "live_mode": False,
    "type": "payment",
    "user_id": 3106807171
}

try:
    resp_web = requests.post(webhook_url, json=payload_teste, timeout=5)

    if resp_web.status_code == 200:
        print(
            f"[OK] Webhook MP respondendo corretamente: HTTP {resp_web.status_code}")
    elif resp_web.status_code == 404:
        print(f"❌ [ERRO] Webhook retornou HTTP 404!")
        print(f"   👉 A rota '/pagamentos/webhook' não existe no seu FastAPI.")
    elif resp_web.status_code == 502:
        print(f"⚠️ [AVISO] Webhook retornou HTTP 502 (Container reiniciando).")
    else:
        print(f"[INFO] Resposta do Webhook MP: HTTP {resp_web.status_code}")
        print("   👉 Se retornou 400 ou 401, a rota existe! Só falta a chave MERCADO_PAGO_WEBHOOK_SECRET no Railway.")

except requests.exceptions.RequestException as e:
    print(f"⚠️ [AVISO] Webhook não respondeu ou deu timeout: {e}")

print("\n--- Validação Concluída ---")
