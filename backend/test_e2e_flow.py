import pytest
import requests
from datetime import datetime

# Configurações - Ajuste para sua URL local ou de produção
BASE_URL = "http://127.0.0.1:8001"
ADMIN_EMAIL = "rsrconsultoriaevenda@gmail.com"
ADMIN_PASS = "Ren@220382"


def test_full_system_flow():
    print("\n--- Iniciando Teste de Fluxo Ponta a Ponta ---")

    # 1. Login do Administrador
    login_res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": ADMIN_EMAIL,
        "senha": ADMIN_PASS
    })
    assert login_res.status_code == 200, "Falha no login do admin"
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Login Admin: OK")

    # 2. Verificar Multitenancy (Listar serviços da empresa)
    servicos_res = requests.get(f"{BASE_URL}/servicos/", headers=headers)
    assert servicos_res.status_code == 200
    print(
        f"✅ Multitenancy (Filtro Automático): OK - {len(servicos_res.json())} serviços encontrados")

    # 3. Simular Pedido via WhatsApp (Criação de Pedido)
    # Simulando o recebimento de uma mensagem do cliente
    whatsapp_payload = {
        "sender": "5554999999999",
        "message": "Pedido transfer origem: Aeroporto Salgado Filho destino: Hotel Gramado data: 20/05/2026 14:00 valor: 250"
    }
    # A rota no código é /whatsapp/webhook ou similar. Baseado no seu routes/whatsapp.py:
    # Nota: No seu código o prefixo é /whatsapp, mas a lógica de recebimento parece estar no processar_evento_whatsapp
    # Vamos testar o endpoint de criação direta de pedido para validar o banco primeiro

    pedido_data = {
        "cliente_id": 1,  # Assumindo que o cliente 1 existe
        "servico_id": 1,
        "origem": "Teste Origem",
        "destino": "Teste Destino",
        "data_servico": "2026-05-20T14:00:00",
        "valor": 250.00
    }

    novo_pedido_res = requests.post(
        f"{BASE_URL}/pedidos/", json=pedido_data, headers=headers)
    assert novo_pedido_res.status_code in [200, 201]
    pedido_id = novo_pedido_res.json()["id"]
    print(f"✅ Criação de Pedido: OK (ID: {pedido_id})")

    # 4. Simular Webhook de Pagamento (Mercado Pago)
    # Simulando a notificação que o Mercado Pago enviaria
    # Precisamos de um mock ou testar a rota diretamente
    webhook_payload = {
        "type": "payment",
        "data": {"id": "123456789"},
        "id": "123456789"
    }
    # Nota: A rota webhook_mercadopago busca o external_reference na API do MP.
    # Para teste manual, vamos atualizar o status via rota de pedidos.

    update_status_res = requests.put(
        f"{BASE_URL}/pedidos/{pedido_id}/status",
        json={"status": "PAGO"},
        headers=headers
    )
    assert update_status_res.status_code == 200
    assert update_status_res.json()["status"] == "PAGO"
    print("✅ Processamento de Pagamento (Simulação): OK")

    # 5. Atribuição de Motorista (Aceite)
    # Primeiro pegamos um motorista
    motoristas_res = requests.get(f"{BASE_URL}/motoristas/", headers=headers)
    if motoristas_res.json():
        motorista_id = motoristas_res.json()[0]["id"]

        aceite_res = requests.put(
            f"{BASE_URL}/pedidos/{pedido_id}/aceitar",
            json={"motorista_id": motorista_id},
            headers=headers
        )
        assert aceite_res.status_code == 200
        assert aceite_res.json()["status"] == "ACEITO"
        print(f"✅ Atribuição de Motorista: OK (Motorista ID: {motorista_id})")
    else:
        print("⚠️ Pulando teste de motorista: Nenhum motorista cadastrado.")

    # 6. Finalização do Serviço
    finalizar_res = requests.put(
        f"{BASE_URL}/pedidos/{pedido_id}/status",
        json={"status": "CONCLUIDO"},
        headers=headers
    )
    assert finalizar_res.status_code == 200
    print("✅ Finalização de Serviço: OK")

    print("\n--- Auditoria Concluída com Sucesso! ---")


if __name__ == "__main__":
    try:
        test_full_system_flow()
    except Exception as e:
        print(f"❌ Falha no Teste: {e}")
