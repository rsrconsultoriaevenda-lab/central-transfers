import sys
import requests

# 1. DEFINIÇÃO DA URL BASE
# Ajuste para a URL do Render conforme o seu uso atual
url = "https://central-transfers-backend.onrender.com"
health_url = f"{url}/api/health"
webhook_url = f"{url}/api/pagamentos/webhook"

print("\n--- 1. Iniciando Validação do Ambiente de Produção ---")
print(f"[INFO] Testando rota principal: {health_url}")

try:
    resp = requests.get(health_url, timeout=10)
    if resp.status_code == 200:
        print(f"[OK] Status Geral: Sistema pronto para uso (HTTP 200).")
    else:
        print(
            f"❌ [ERRO] API ({health_url}) retornou status {resp.status_code}")
except requests.exceptions.RequestException as e:
    print(f"❌ [ERRO] Não foi possível conectar à API principal: {e}")

print("\n--- 2. Verificando Webhook Mercado Pago ---")
print(f"[INFO] Testando endpoint: {webhook_url}")

payload_teste = {
    "action": "payment.updated",
    "type": "payment",
    "data": {"id": "123456"}
}

try:
    resp_web = requests.post(webhook_url, json=payload_teste, timeout=10)
    if resp_web.status_code == 200:
        print(f"[OK] Webhook MP respondendo corretamente: HTTP 200")
    elif resp_web.status_code == 403:
        print(f"[OK] Rota existe, mas acesso negado (Esperado sem HMAC válido).")
    else:
        print(f"[INFO] Resposta do Webhook: HTTP {resp_web.status_code}")
except requests.exceptions.RequestException as e:
    print(f"⚠️ [AVISO] Webhook não respondeu: {e}")

print("\n--- Validação Concluída ---")
