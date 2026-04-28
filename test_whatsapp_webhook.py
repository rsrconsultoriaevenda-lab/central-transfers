import requests
import json

BASE_URL = "http://127.0.0.1:8001"
VERIFY_TOKEN = "central-transfers-2026" # Deve ser o mesmo do seu .env

def test_webhook_verification():
    print("\n--- Testando Verificação (GET /webhook) ---")
    params = {
        "hub.mode": "subscribe",
        "hub.verify_token": VERIFY_TOKEN,
        "hub.challenge": "123456789"
    }
    try:
        response = requests.get(f"{BASE_URL}/webhook", params=params)
        if response.status_code == 200 and response.text == "123456789":
            print("✅ Handshake validado com sucesso!")
        else:
            print(f"❌ Falha na validação. Status: {response.status_code}, Resposta: {response.text}")
    except Exception as e:
        print(f"💥 Erro de conexão: {e}")

def test_message_processing():
    print("\n--- Testando Recebimento de Mensagem (POST /webhook) ---")
    # Payload simulando o formato real da Meta API
    payload = {
        "object": "whatsapp_business_account",
        "entry": [{
            "id": "WHATSAPP_BUSINESS_ACCOUNT_ID",
            "changes": [{
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"display_phone_number": "123456789", "phone_number_id": "123456789"},
                    "contacts": [{"profile": {"name": "Usuario Teste"}, "wa_id": "5554999999999"}],
                    "messages": [{
                        "from": "5554999999999",
                        "id": "wamid.HBgLNTU1NDk5OTk5OTk5OQ==",
                        "timestamp": "1645454545",
                        "text": {"body": "Pedido transfer origem: Aeroporto destino: Hotel data: 30/04/2026 10:00 valor: 200"},
                        "type": "text"
                    }]
                },
                "field": "messages"
            }]
        }]
    }
    
    try:
        response = requests.post(f"{BASE_URL}/webhook", json=payload)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.json()}")
        if response.status_code == 200:
            print("✅ Payload de mensagem enviado para processamento.")
    except Exception as e:
        print(f"💥 Erro ao processar mensagem: {e}")

def test_button_reply():
    print("\n--- Testando Resposta de Botão (Aceitar Pedido) ---")
    payload = {
        "entry": [{
            "changes": [{
                "value": {
                    "messages": [{
                        "from": "5554888888888",
                        "type": "interactive",
                        "interactive": {
                            "type": "button_reply",
                            "button_reply": {"id": "ACEITAR_PEDIDO_1", "title": "Aceitar ✅"}
                        }
                    }]
                }
            }]
        }]
    }
    requests.post(f"{BASE_URL}/webhook", json=payload)
    print("✅ Simulação de 'Aceitar Pedido' enviada.")

if __name__ == "__main__":
    test_webhook_verification()
    test_message_processing()
    test_button_reply()