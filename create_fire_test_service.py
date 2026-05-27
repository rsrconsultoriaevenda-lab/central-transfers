import requests
import os
from dotenv import load_dotenv

load_dotenv()

# Use a URL do Render
# DICA: Verifique se o seu backend oficial é Render ou Railway e ajuste aqui:
RENDER_URL = "https://central-transfers-backend.onrender.com/api"
API_URL = os.getenv("VITE_API_URL") or RENDER_URL
# Garante que a URL da API sempre termine com /api
if not API_URL.endswith("/api"):
    API_URL = API_URL.rstrip("/") + "/api"

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASS = os.getenv("ADMIN_PASS")


def create_test_item():
    print("\n" + "="*50)
    print(f"📡 AUDITORIA DE AMBIENTE")
    print(
        f"📍 VITE_API_URL no .env: {os.getenv('VITE_API_URL', 'NÃO DEFINIDA')}")
    print(f"👤 ADMIN_EMAIL: {ADMIN_EMAIL or '❌ NÃO CARREGADO'}")
    print(
        f"🔑 ADMIN_PASS: {'*' * len(ADMIN_PASS) if ADMIN_PASS else '❌ NÃO CARREGADO'}")
    print(f"🚀 ALVO FINAL DO SCRIPT: {API_URL}")
    print("="*50 + "\n")

    if not ADMIN_EMAIL or not ADMIN_PASS:
        print("❌ ERRO: Credenciais de ADMIN não encontradas no .env")
        return

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

    # Adicionada a barra final '/' para evitar problemas de redirecionamento 307/401
    res = requests.post(f"{API_URL}/servicos/",
                        data=service_data, headers=headers)
    if res.status_code in [200, 201]:
        print("✅ Serviço de Teste (R$ 1,00) criado com sucesso!")
    else:
        print(f"❌ Erro ao criar serviço: {res.text}")


if __name__ == "__main__":
    create_test_item()
