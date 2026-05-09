# backend/conftest.py

import pytest
import requests

BASE_URL = "http://127.0.0.1:8001"

ADMIN_EMAIL = "rsrconsultoriaevenda@gmail.com"
ADMIN_PASS = "Ren@220382"


@pytest.fixture(scope="session")
def api_session():
    """
    Cria uma sessão autenticada para reutilização nos testes.
    """

    session = requests.Session()

    login_payload = {
        "email": ADMIN_EMAIL,
        "senha": ADMIN_PASS
    }

    try:
        response = session.post(
            f"{BASE_URL}/auth/login",
            json=login_payload,
            timeout=5
        )
    except requests.exceptions.ConnectionError:
        pytest.fail(
            f"❌ Erro de conexão: O servidor em {BASE_URL} não está rodando."
        )

    assert response.status_code == 200, (
        f"Falha no login: {response.status_code} - {response.text}"
    )

    data = response.json()
    token = data.get("access_token")

    assert token, "Token JWT não retornado pela API."

    session.headers.update({
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    })

    return session


@pytest.fixture
def motorista_teste(api_session):
    """
    Cria um motorista válido para os testes E2E.
    """

    payload = {
        "nome": "Motorista Teste",
        "telefone": "11999999999",
        "ativo": True,
        "carro": "Toyota Corolla",
        "placa": "ABC1D23",
        "modelo": "Corolla",
        "ano": 2022,
        "plano": "MASTER"
    }

    response = api_session.post(
        f"{BASE_URL}/motoristas",
        json=payload
    )

    assert response.status_code in [200, 201], (
        f"Erro ao criar motorista: "
        f"{response.status_code} - {response.text}"
    )

    return response.json()
