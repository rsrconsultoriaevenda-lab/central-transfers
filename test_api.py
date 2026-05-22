import requests
import pytest
import os

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8001")


def test_health_check_servidor():
    url = f"{BASE_URL}/health"
    response = requests.get(url)
    print(f"\nConteúdo da resposta: {response.json()}")
    assert response.status_code == 200
    assert response.json() is not None


def test_listar_pedidos_formato():
    url = f"{BASE_URL}/pedidos/"
    response = requests.get(url)
    assert response.status_code in [200, 401]
    assert isinstance(response.json(), (list, dict))


def test_tentativa_login_sucesso():
    url = f"{BASE_URL}/auth/login"
    dados = {
        "email": "rsrconsultoriaevenda@gmail.com",
        "senha": "Ren@220382"
    }
    response = requests.post(url, json=dados)
    print(f"\nStatus: {response.status_code}")
    print(f"Resposta: {response.json()}")
    assert response.status_code == 200


def test_criar_pedido_transfer_sucesso():
    # 1. Primeiro fazemos o login para pegar o token
    url_login = f"{BASE_URL}/auth/login"
    login_data = {
        "email": "rsrconsultoriaevenda@gmail.com",
        "senha": "Ren@220382"
    }

    login_res = requests.post(url_login, json=login_data)

    # Verificação de segurança para o token
    if login_res.status_code != 200:
        print(f"\nErro no Login do Pedido: {login_res.status_code}")
        print(f"Detalhe: {login_res.json()}")
        pytest.fail("Não foi possível obter o token para criar o pedido")

    token = login_res.json()["access_token"]

    # 2. Agora criamos o pedido usando o Token obtido
    url_pedido = f"{BASE_URL}/pedidos/"
    headers = {"Authorization": f"Bearer {token}"}

    pedido_data = {
        "cliente_id": 1,  # Certifique-se de que o ID exista ou use o seed
        "servico_id": 1,
        "origem": "Aeroporto Salgado Filho (POA)",
        "destino": "Hotel Serra Azul - Gramado",
        "data_servico": "2026-05-15T14:30:00",
        "valor": 250.00
    }

    response = requests.post(url_pedido, json=pedido_data, headers=headers)

    assert response.status_code in [200, 201]
