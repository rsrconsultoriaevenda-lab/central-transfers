import requests
import json

# Altere para a URL do seu deploy no Railway ou localhost para testes locais
BASE_URL = "https://central-transfers-production.up.railway.app"

def simular_webhook_pagamento(payment_id="5500112233"):
    """
    Simula a notificação de IPN/Webhook que o Mercado Pago envia.
    Nota: O backend tentará consultar este ID na API do MP, então 
    para um teste real de ponta a ponta, use um ID de sandbox válido.
    """
    print(f"\n--- Enviando Webhook de Pagamento para {BASE_URL} ---")
    
    payload = {
        "type": "payment",
        "data": {
            "id": payment_id
        }
    }

    try:
        response = requests.post(
            f"{BASE_URL}/pagamentos/webhook/mercadopago", 
            json=payload,
            timeout=10
        )
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        print("\n✅ Verifique os logs do Railway. Você deve ver:")
        print("1. O pedido sendo marcado como PAGO.")
        print("2. A notificação enviada ao cliente.")
        print("3. O broadcast para os motoristas ativos.")
    except Exception as e:
        print(f"💥 Erro ao conectar: {e}")

if __name__ == "__main__":
    simular_webhook_pagamento()