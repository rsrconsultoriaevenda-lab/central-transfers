import pytest
import requests
import time
import os
from fastapi.testclient import TestClient
from backend.main import app
from backend.database import SessionLocal

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8001")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "rsrconsultoriaevenda@gmail.com")
ADMIN_PASS = os.getenv("ADMIN_PASS", "Ren@220382")


@pytest.fixture(scope="session", autouse=True)
def start_test_server():
    """
    Fixture inteligente: aguarda até o servidor FastAPI responder em `/docs`.
    Se não estiver pronto dentro do timeout, falha explicitamente.

    Esta fixture é um generator (usa `yield`) para compatibilidade com pytest-asyncio.
    """
    timeout = 15
    start_time = time.time()
    connected = False

    print("\n[Pytest] 🔍 Aguardando inicialização do servidor Central Transfers...")

    while time.time() - start_time < timeout:
        try:
            # Testamos a rota de documentação que é leve e nativa do FastAPI
            resp = requests.get(f"{BASE_URL}/docs", timeout=1)
            if resp.status_code == 200:
                connected = True
                break
        except requests.exceptions.ConnectionError:
            # servidor ainda não pronto, aguarda um pouco e tenta novamente
            time.sleep(0.5)

    if not connected:
        pytest.fail(
            "❌ O servidor na porta 8005 não ficou pronto a tempo para os testes.")

    # Se chegamos aqui, o servidor está pronto — entregamos controle aos testes
    yield None

    # Teardown (se necessário) pode ir aqui


@pytest.fixture(scope="session")
def api_session(start_test_server):
    """Garante o login administrativo usando a sessão de pé."""
    session = requests.Session()
    try:
        response = session.post(
            f"{BASE_URL}/auth/login", json={"email": ADMIN_EMAIL, "senha": ADMIN_PASS}, timeout=15)
    except requests.exceptions.ConnectionError:
        pytest.fail(f"❌ Conexão recusada ao tentar autenticar em {BASE_URL}")
    except requests.exceptions.Timeout:
        pytest.fail(
            f"❌ Timeout ao tentar autenticar em {BASE_URL} (Servidor muito lento)")

    assert response.status_code == 200, f"❌ Erro login admin: {response.text}"
    token = response.json().get("access_token")
    session.headers.update(
        {"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
    return session


@pytest.fixture
def client():
    """Retorna um TestClient para testes de integração direta com o app."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """Cria uma sessão de banco de dados para testes unitários."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def auth_headers(api_session):
    """Retorna um dicionário com os headers de autorização obtidos no login."""
    return dict(api_session.headers)


@pytest.fixture
def motorista_teste(api_session):
    """Gera um motorista aleatório dinâmico para os testes de integração."""
    id_unico = str(int(time.time()))[-6:]
    payload = {
        "nome": f"Motorista Teste {id_unico}",
        "telefone": f"54999{id_unico}",
        "ativo": True,
        "carro": "Toyota Corolla",
        "placa": f"ABC{id_unico[0]}D{id_unico[1:3]}",
        "modelo": "Corolla",
        "ano": 2022,
        "plano": "MASTER",
        "senha": "Ren@220382"
    }
    response = api_session.post(
        f"{BASE_URL}/motoristas/register", json=payload)
    assert response.status_code in [
        200, 201], f"❌ Erro criar motorista: {response.text}"
    return response.json()
