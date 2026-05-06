import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"
ADMIN_EMAIL = "rsrconsultoriaevenda@gmail.com"
ADMIN_PASS = "Ren@220382"


def executar_teste_pedido():
    print("\n📦 Iniciando Teste de Fluxo: Criação de Pedido")
    print("-" * 50)

    # 1. Login para obter Token
    print("🔑 Realizando login...")
    auth_res = requests.post(
        f"{BASE_URL}/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_PASS})
    if auth_res.status_code != 200:
        print(f"❌ Erro no login: {auth_res.text}")
        return

    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Autenticado com sucesso.")

    # 2. Criar um Cliente (Necessário para vincular ao pedido)
    print("👤 Criando cliente de teste...")
    cliente_data = {
        "nome": "Cliente Teste Fluxo",
        "telefone": "54999998888",
        "email": "cliente.teste@gmail.com"
    }
    client_res = requests.post(
        f"{BASE_URL}/clientes/", json=cliente_data, headers=headers)
    cliente_id = client_res.json()["id"]
    print(f"✅ Cliente criado ID: {cliente_id}")

    # 3. Obter um Serviço existente (Seed)
    print("🚗 Buscando serviços disponíveis...")
    serv_res = requests.get(f"{BASE_URL}/servicos/", headers=headers)
    servicos = serv_res.json()
    if not servicos:
        print("❌ Nenhum serviço encontrado. Rode o seed_db.py primeiro.")
        return

    servico_id = servicos[0]["id"]
    print(f"✅ Usando serviço: {servicos[0]['nome']} (ID: {servico_id})")

    # 4. Criar o Pedido
    print("📝 Enviando novo pedido...")
    data_servico = (datetime.now() + timedelta(days=2)
                    ).strftime("%Y-%m-%dT14:00:00")

    pedido_payload = {
        "cliente_id": cliente_id,
        "servico_id": servico_id,
        "origem": "Aeroporto Salgado Filho",
        "destino": "Hotel Ritta Höppner, Gramado",
        "data_servico": data_servico,
        "valor": 280.00,
        "valor_comissao": 56.00,
        "observacoes": "Teste de integração automatizado"
    }

    res_pedido = requests.post(
        f"{BASE_URL}/pedidos/", json=pedido_payload, headers=headers)

    if res_pedido.status_code in [200, 201]:
        data = res_pedido.json()
        print("🚀 SUCESSO! Pedido criado.")
        print(f"🆔 ID do Pedido: {data['id']}")
        print(f"📊 Status: {data['status']}")
        print(
            f"🏢 Empresa ID (Multitenancy): {data.get('empresa_id', 'Não retornado')}")
    else:
        print(f"❌ Erro ao criar pedido: {res_pedido.status_code}")
        print(res_pedido.text)


if __name__ == "__main__":
    try:
        executar_teste_pedido()
    except requests.exceptions.ConnectionError:
        print("❌ Servidor offline. Rode o run_dev.py primeiro.")
    except Exception as e:
        print(f"💥 Erro inesperado: {e}")
