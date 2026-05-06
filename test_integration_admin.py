import requests
import json

# Configurações do ambiente local
BASE_URL = "http://localhost:8001"
ADMIN_EMAIL = "rsrconsultoriaevenda@gmail.com"
ADMIN_PASS = "Ren@220382"


def test_admin_and_driver_flow():
    print("\n🚀 Iniciando Teste de Integração: Fluxo Admin -> Motorista")
    print("-" * 60)

    # 1. Simular Login do Administrador
    login_url = f"{BASE_URL}/auth/login"
    login_data = {
        "email": ADMIN_EMAIL,
        "senha": ADMIN_PASS
    }

    try:
        print(f"🔑 Tentando login como admin: {ADMIN_EMAIL}...")
        response = requests.post(login_url, json=login_data, timeout=10)

        if response.status_code != 200:
            print(
                f"❌ Falha no login: {response.status_code} - {response.text}")
            return

        token = response.json().get("access_token")
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Login realizado! Token JWT obtido.")

        # 2. Simular Cadastro de um Novo Motorista via Dashboard (Admin)
        motorista_url = f"{BASE_URL}/motoristas/"
        # Dados baseados no MotoristaBase schema
        payload = {
            "nome": "Motorista de Teste Integração",
            "telefone": "54912345678",
            "carro": "Toyota Corolla",
            "placa": "BRA2E24",
            "modelo": "XEI",
            "ano": 2024,
            "categoria": "PREMIUM",
            "plano": "MASTER"
        }

        print(f"📝 Enviando cadastro para {motorista_url}...")
        res_motorista = requests.post(
            motorista_url, json=payload, headers=headers, timeout=10)

        if res_motorista.status_code == 201:
            data = res_motorista.json()
            print("✅ Sucesso! Resposta da API (201 Created):")
            print(json.dumps(data, indent=4, ensure_ascii=False))
            print(
                f"\n💡 Senha gerada para o motorista: {data['acesso']['senha']}")
        elif res_motorista.status_code == 400:
            print(
                f"⚠️ Erro de Validação: {res_motorista.json().get('detail')}")
        else:
            print(
                f"❌ Erro inesperado: {res_motorista.status_code} - {res_motorista.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor. O FastAPI está rodando na porta 8001?")
    except Exception as e:
        print(f"💥 Erro durante o teste: {e}")


if __name__ == "__main__":
    test_admin_and_driver_flow()
