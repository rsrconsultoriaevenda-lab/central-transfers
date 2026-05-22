import pytest
from backend.models import Servico, Cliente


def test_criar_pedido_sucesso(client, db_session, auth_headers):
    # Setup: Criar dados necessários
    servico = Servico(nome="Transfer Teste", valor=150.00)
    cliente = Cliente(nome="João Silva", telefone="51999999999")
    db_session.add(servico)
    db_session.add(cliente)
    db_session.commit()

    payload = {
        "cliente_id": cliente.id,
        "servico_id": servico.id,
        "origem": "Aeroporto",
        "destino": "Hotel Centro",
        "data_servico": "2024-12-25T10:00:00",
        "valor": 150.00
    }

    response = client.post("/pedidos/", json=payload, headers=auth_headers)

    assert response.status_code == 201
    data = response.json()
    assert data["origem"] == "Aeroporto"
    assert data["status"] == "PENDENTE"


def test_listar_pedidos_protegido(client):
    """Garante que a rota de listagem exige autenticação."""
    response = client.get("/pedidos/")
    assert response.status_code == 401
