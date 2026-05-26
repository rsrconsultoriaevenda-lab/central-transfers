import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Use a URL do Render
API_URL = "https://central-transfers-backend.onrender.com/api"
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASS = os.getenv("ADMIN_PASS")


def create_test_item():
    print(f"🚀 Conectando em: {API_URL}")

    # 1. Login
    login_res = requests.post(f"{API_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "senha": ADMIN_PASS
    })

    if login_res.status_code != 200:
        print("❌ Falha no login. Verifique as credenciais no .env")
        return

    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Criar Serviço de R$ 1,00
    service_data = {
        "nome": "🔥 TESTE DE FOGO 1.0",
        "categoria": "TRANSFERS",
        "valor": 1.00,
        "descricao": "Serviço para validação de fluxo real de pagamento e webhook."
    }

    res = requests.post(f"{API_URL}/servicos",
                        data=service_data, headers=headers)
    if res.status_code in [200, 201]:
        print("✅ Serviço de Teste (R$ 1,00) criado com sucesso!")
    else:
        print(f"❌ Erro ao criar serviço: {res.text}")


if __name__ == "__main__":
    create_test_item()
