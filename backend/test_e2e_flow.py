import pytest
import requests
import os
from typing import Dict

# Configurações via variáveis de ambiente com fallback para desenvolvimento
BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8001")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "rsrconsultoriaevenda@gmail.com")
ADMIN_PASS = os.getenv("ADMIN_PASS", "Ren@220382")


def test_full_system_flow(api_session, motorista_teste):
    print("\n--- Iniciando Teste de Fluxo Ponta a Ponta ---")

    # 1. Verificar Multitenancy (Listar serviços da empresa)
    servicos_res = api_session.get(f"{BASE_URL}/servicos/")
    servicos_res.raise_for_status()
    servicos = servicos_res.json()
    assert isinstance(servicos, list)
    print(
        f"✅ Multitenancy (Filtro Automático): OK - {len(servicos)} serviços encontrados")

    # 2. Criação de Pedido
    # Tenta obter um cliente e serviço reais para o teste não quebrar em bancos limpos
    clientes_res = api_session.get(f"{BASE_URL}/clientes/")
    clientes = clientes_res.json()

    if not clientes or not servicos:
        pytest.fail(
            "❌ Erro: O banco de dados precisa de ao menos um cliente e um serviço. Rode 'python seed_db.py' primeiro.")

    target_cliente_id = clientes[0]["id"]
    target_servico_id = servicos[0]["id"]

    pedido_data = {
        "cliente_id": target_cliente_id,
        "servico_id": target_servico_id,
        "origem": "Aeroporto Salgado Filho",
        "destino": "Hotel Gramado",
        "data_servico": "2026-05-20T14:00:00",
        "valor": 250.00
    }

    novo_pedido_res = api_session.post(
        f"{BASE_URL}/pedidos/", json=pedido_data)
    assert novo_pedido_res.status_code in [200, 201]
    pedido = novo_pedido_res.json()
    pedido_id = pedido["id"]
    print(f"✅ Criação de Pedido: OK (ID: {pedido_id})")

    # 3. Simular Webhook de Pagamento (Transição de Status)
    update_status_res = api_session.put(
        f"{BASE_URL}/pedidos/{pedido_id}/status",
        json={"status": "PAGO"}
    )
    update_status_res.raise_for_status()
    assert update_status_res.json()["status"] == "PAGO"
    print("✅ Processamento de Pagamento (Simulação): OK")

    # 4. Atribuição de Motorista (Aceite)
    motoristas_res = api_session.get(f"{BASE_URL}/motoristas/")
    motoristas_res.raise_for_status()
    motoristas = motoristas_res.json()

    if motoristas:
        motorista_id = motorista_teste["motorista"]["id"]
        aceite_res = api_session.put(
            f"{BASE_URL}/pedidos/{pedido_id}/aceitar",
            json={"motorista_id": motorista_id}
        )
        aceite_res.raise_for_status()
        assert aceite_res.json()["status"] == "ACEITO"
        print(f"✅ Atribuição de Motorista: OK (Motorista ID: {motorista_id})")
    else:
        print("⚠️ Atenção: Nenhum motorista disponível para teste de aceite.")

    # 5. Finalização do Serviço
    finalizar_res = api_session.put(
        f"{BASE_URL}/pedidos/{pedido_id}/status",
        json={"status": "CONCLUIDO"}
    )
    finalizar_res.raise_for_status()
    assert finalizar_res.json()["status"] == "CONCLUIDO"
    print("✅ Finalização de Serviço: OK")

    print("\n--- Auditoria Concluída com Sucesso! ---")


if __name__ == "__main__":
    # Permite rodar o arquivo diretamente via 'python backend/test_e2e_flow.py'
    import sys
    sys.exit(pytest.main([__file__, "-s"]))
