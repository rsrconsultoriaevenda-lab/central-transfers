import requests
import json
from datetime import datetime, timedelta

BASE_URL = "http://localhost:8001"
ADMIN_EMAIL = "rsrconsultoriaevenda@gmail.com"
ADMIN_PASS = "Ren@220382"


def testar_fluxo_e2e():
    print("\n🚀 Iniciando Teste de Fluxo Completo (E2E)")
    print("=" * 60)

    # 1. Login do Administrador
    print("🔑 Efetuando login...")
    auth_res = requests.post(
        f"{BASE_URL}/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_PASS})
    if auth_res.status_code != 200:
        print(f"❌ Erro no login: {auth_res.text}")
        return

    token = auth_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Autenticado.")

    # 2. Obter Cliente e Serviço
    print("🔍 Verificando dependências (Cliente e Serviço)...")

    res_clients = requests.get(f"{BASE_URL}/clientes/", headers=headers)
    if res_clients.status_code != 200:
        print(
            f"❌ Erro ao buscar clientes ({res_clients.status_code}). Verifique se a rota '/clientes/' existe no backend.")
        return
    clients = res_clients.json()

    res_services = requests.get(f"{BASE_URL}/servicos/", headers=headers)
    if res_services.status_code != 200:
        print(
            f"❌ Erro ao buscar serviços ({res_services.status_code}). Verifique se a rota '/servicos/' existe no backend.")
        return
    services = res_services.json()

    if not clients or not services:
        print("⚠️  Nenhum cliente ou serviço encontrado. Rode o 'python seed_db.py' primeiro para popular o banco.")
        return

    cliente_id = clients[0]["id"]
    servico_id = services[0]["id"]
    print(f"✅ Usando Cliente ID: {cliente_id} | Serviço ID: {servico_id}")

    # 3. Criação do Pedido (Fluxo Cliente)
    print("\n📝 [CLIENTE] Criando novo pedido...")
    data_servico = (datetime.now() + timedelta(days=1)
                    ).strftime("%Y-%m-%dT10:00:00")
    pedido_payload = {
        "cliente_id": cliente_id,
        "servico_id": servico_id,
        "origem": "Aeroporto Salgado Filho",
        "destino": "Gramado Centro",
        "data_servico": data_servico,
        "valor": 300.00,
        "valor_comissao": 60.00,
        "observacoes": "Teste E2E automatizado"
    }
    res_pedido = requests.post(
        f"{BASE_URL}/pedidos/", json=pedido_payload, headers=headers)
    pedido_id = res_pedido.json()["id"]
    print(
        f"✅ Pedido #{pedido_id} criado com status: {res_pedido.json()['status']}")

    # 4. Simulação de Pagamento
    print(
        f"💳 [SISTEMA] Simulando confirmação de pagamento para o Pedido #{pedido_id}...")
    res_pagto = requests.put(
        f"{BASE_URL}/pedidos/{pedido_id}/status",
        json={"status": "PAGO"},
        headers=headers
    )
    print(f"✅ Status atualizado para: {res_pagto.json()['status']}")

    # 5. Aceite do Motorista (Fluxo Motorista)
    print("\n🚖 [MOTORISTA] Buscando motorista disponível...")
    drivers = requests.get(f"{BASE_URL}/motoristas/", headers=headers).json()
    if not drivers:
        print("⚠️ Aviso: Nenhum motorista cadastrado. Teste de aceite ignorado.")
        return

    motorista_id = drivers[0]["id"]
    print(
        f"📝 Motorista {drivers[0]['nome']} (ID: {motorista_id}) tentando aceitar o pedido...")

    res_aceite = requests.put(
        f"{BASE_URL}/pedidos/{pedido_id}/aceitar",
        json={"motorista_id": motorista_id},
        headers=headers
    )

    if res_aceite.status_code == 200:
        print(f"✅ Pedido aceito! Status: {res_aceite.json()['status']}")
    else:
        print(f"❌ Erro no aceite: {res_aceite.text}")
        return

    # 6. Conclusão do Serviço
    print(f"\n🏁 [MOTORISTA] Finalizando o serviço #{pedido_id}...")
    res_concluir = requests.put(
        f"{BASE_URL}/pedidos/{pedido_id}/status",
        json={"status": "CONCLUIDO"},
        headers=headers
    )

    if res_concluir.status_code == 200:
        final_data = res_concluir.json()
        print("🚀 SUCESSO! Fluxo completo finalizado.")
        print("-" * 60)
        print(f"Resumo Final:")
        print(f"  - Pedido ID: {final_data['id']}")
        print(f"  - Status Final: {final_data['status']}")
        print(f"  - Motorista Atribuído: {final_data.get('motorista_id')}")
        print(f"  - Valor Total: R$ {final_data['valor']}")
    else:
        print(f"❌ Erro ao concluir: {res_concluir.text}")


if __name__ == "__main__":
    try:
        # Verifica se o backend está acessível
        requests.get(f"{BASE_URL}/", timeout=2)
        testar_fluxo_e2e()
    except requests.exceptions.ConnectionError:
        print("❌ Servidor offline na porta 8001. Execute o 'run_dev.py' primeiro.")
    except Exception as e:
        print(f"💥 Erro inesperado: {e}")
