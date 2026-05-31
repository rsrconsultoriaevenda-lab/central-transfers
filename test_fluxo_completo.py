import requests
import os
from datetime import datetime, timedelta

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8001").rstrip('/')

ADMIN_EMAIL = "rsrconsultoriaevenda@gmail.com"
ADMIN_PASS = "Ren@220382"


def testar_fluxo_e2e():
    print("\n🚀 Iniciando Teste de Fluxo Completo (E2E)")
    print("=" * 60)

    # 1. Login do Administrador
    print("🔑 Efetuando login...")

    print(f"POST => {BASE_URL}/auth/login")
    print({
        "email": ADMIN_EMAIL,
        "senha": ADMIN_PASS
    })

    auth_res = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": ADMIN_EMAIL,
            "senha": ADMIN_PASS
        }
    )

    print(f"STATUS: {auth_res.status_code}")
    print(f"RESPOSTA: {auth_res.text}")

    if auth_res.status_code != 200:
        print(f"❌ Erro no login: {auth_res.text}")
        return

    token = auth_res.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    print("✅ Autenticado.")

    # 2. Obter Cliente e Serviço
    print("\n🔍 Verificando dependências (Cliente e Serviço)...")

    res_clients = requests.get(
        f"{BASE_URL}/clientes/",
        headers=headers
    )

    print(f"Clientes Status: {res_clients.status_code}")

    if res_clients.status_code != 200:
        print(
            f"❌ Erro ao buscar clientes: {res_clients.text}"
        )
        return

    clients = res_clients.json()

    res_services = requests.get(
        f"{BASE_URL}/servicos/",
        headers=headers
    )

    print(f"Serviços Status: {res_services.status_code}")

    if res_services.status_code != 200:
        print(
            f"❌ Erro ao buscar serviços: {res_services.text}"
        )
        return

    services = res_services.json()

    if not clients or not services:
        print(
            "⚠️ Nenhum cliente ou serviço encontrado. Rode o seed_db.py."
        )
        return

    cliente_id = clients[0]["id"]
    servico_id = services[0]["id"]

    print(
        f"✅ Usando Cliente ID: {cliente_id} | Serviço ID: {servico_id}"
    )

    # 3. Criar Pedido
    print("\n📝 [CLIENTE] Criando novo pedido...")

    data_servico = (
        datetime.now() + timedelta(days=1)
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
        f"{BASE_URL}/pedidos/",
        json=pedido_payload,
        headers=headers
    )

    print(f"Pedido Status: {res_pedido.status_code}")
    print(f"Pedido Resposta: {res_pedido.text}")

    if res_pedido.status_code not in [200, 201]:
        print("❌ Falha ao criar pedido")
        return

    pedido_data = res_pedido.json()
    pedido_id = pedido_data["id"]

    print(
        f"✅ Pedido #{pedido_id} criado com status: {pedido_data['status']}"
    )

    # 4. Simular pagamento
    print(
        f"\n💳 [SISTEMA] Confirmando pagamento do Pedido #{pedido_id}..."
    )

    res_pagto = requests.put(
        f"{BASE_URL}/pedidos/{pedido_id}/status",
        json={"status": "PAGO"},
        headers=headers
    )

    print(f"Pagamento Status: {res_pagto.status_code}")
    print(f"Pagamento Resposta: {res_pagto.text}")

    if res_pagto.status_code != 200:
        print("❌ Falha ao atualizar pagamento")
        return

    print(
        f"✅ Status atualizado para: {res_pagto.json()['status']}"
    )

    # 5. Buscar motorista
    print("\n🚖 [MOTORISTA] Buscando motorista disponível...")

    drivers_res = requests.get(
        f"{BASE_URL}/motoristas/",
        headers=headers
    )

    print(f"Motoristas Status: {drivers_res.status_code}")

    if drivers_res.status_code != 200:
        print(f"❌ Erro ao buscar motoristas: {drivers_res.text}")
        return

    drivers = drivers_res.json()

    if not drivers:
        print(
            "⚠️ Nenhum motorista cadastrado. Teste de aceite ignorado."
        )
        return

    # Tenta encontrar o motorista MENSAL para testar a diferença de comissão
    motorista_mensal = next(
        (d for d in drivers if d.get("plano") == "MENSAL"), drivers[0])
    motorista_id = motorista_mensal["id"]

    print(
        f"📝 Motorista {motorista_mensal['nome']} "
        f"(Plano: {motorista_mensal.get('plano')}) "
        f"(ID: {motorista_id}) tentando aceitar o pedido..."
    )

    res_aceite = requests.put(
        f"{BASE_URL}/pedidos/{pedido_id}/aceitar",
        json={"motorista_id": motorista_id},
        headers=headers
    )

    print(f"Aceite Status: {res_aceite.status_code}")
    print(f"Aceite Resposta: {res_aceite.text}")

    if res_aceite.status_code != 200:
        print("❌ Erro no aceite")
        return

    print(
        f"✅ Pedido aceito! Status: {res_aceite.json()['status']}"
    )

    # 6. Finalizar serviço
    print(f"\n🏁 [MOTORISTA] Finalizando serviço #{pedido_id}...")

    res_concluir = requests.put(
        f"{BASE_URL}/pedidos/{pedido_id}/status",
        json={"status": "CONCLUIDO"},
        headers=headers
    )

    print(f"Conclusão Status: {res_concluir.status_code}")
    print(f"Conclusão Resposta: {res_concluir.text}")

    if res_concluir.status_code != 200:
        print("❌ Erro ao concluir serviço")
        return

    final_data = res_concluir.json()

    # 7. Validar Relatório Financeiro (Novo!)
    print("\n📊 [ADMIN] Validando fechamento de caixa...")
    res_financeiro = requests.get(
        f"{BASE_URL}/dashboard/admin/drivers-summary",
        headers=headers
    )

    if res_financeiro.status_code == 200:
        summary = res_financeiro.json()
        # Procura o motorista que usamos no teste
        motorista_stats = next(
            (s for s in summary if s["id"] == motorista_id), None)
        if motorista_stats:
            print(f"✅ Relatório atualizado para {motorista_stats['nome']}:")
            print(f"   - Bruto: R$ {motorista_stats['total_bruto']}")
            print(f"   - Repasse: R$ {motorista_stats['total_repasse']}")
            print(f"   - Corridas: {motorista_stats['corridas']}")
        else:
            print("⚠️ Motorista não encontrado no resumo financeiro.")
    else:
        print(f"❌ Erro ao acessar resumo financeiro: {res_financeiro.text}")

    print("\n🚀 SUCESSO! Fluxo completo finalizado.")
    print("-" * 60)

    print(f"Pedido ID: {final_data['id']}")
    print(f"Status Final: {final_data['status']}")
    print(f"Motorista: {final_data.get('motorista_id')}")
    print(f"Valor Total: R$ {final_data['valor']}")


if __name__ == "__main__":
    try:
        # Verifica se o servidor responde (independente de ser 200 ou 404 na raiz)
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"📡 Conexão estabelecida com: {BASE_URL}")
        testar_fluxo_e2e()

    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print(
            f"\n❌ ERRO: Servidor offline ou inacessível em: {BASE_URL}\n"
            "Certifique-se de que o backend está rodando e a URL (API_URL) está correta."
        )

    except Exception as e:
        print(f"💥 Erro inesperado: {e}")
