# tests/test_whatsapp_webhook.py

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


@pytest.fixture
def payload_text_vagas():
    return {
"entry": [{
    "changes": [{
        "value": {
            "messages": [{
                "from": "5511999999999",
                "text": {"body": "vagas"}
            }]
        }
    }]
}]
}


@pytest.fixture
def payload_saudacao():
    return {
"entry": [{
    "changes": [{
        "value": {
            "messages": [{
                "from": "5511888888888",
                "text": {"body": "Oi"}
            }]
        }
    }]
}]
}


@pytest.fixture
def payload_botao():
    return {
"entry": [{
    "changes": [{
        "value": {
            "messages": [{
                "from": "5511777777777",
                "interactive": {
                    "button_reply": {
                        "id": "aceitar_vaga"
                    }
                }
            }]
        }
    }]
}]
}


@pytest.fixture
def payload_sem_sender():
    return {
"entry": [{
    "changes": [{
        "value": {
            "messages": [{
                "text": {"body": "vagas"}
            }]
        }
    }]
}]
}


@pytest.fixture
def payload_invalido():
    return {}


# ✅ CORREÇÃO AQUI (rota correta)
BASE_URL = "/whatsapp/webhook"


def test_vagas(payload_text_vagas):
    response = client.post(BASE_URL, json=payload_text_vagas)
    assert response.status_code == 200
    assert response.json()["status"] == "vagas_listadas"


def test_saudacao(payload_saudacao):
    response = client.post(BASE_URL, json=payload_saudacao)
    assert response.status_code == 200
    assert response.json()["status"] == "saudacao"


def test_botao_interativo(payload_botao):
    response = client.post(BASE_URL, json=payload_botao)
    assert response.status_code == 200
    assert response.json()["status"] == "botao_processado"


def test_sem_sender(payload_sem_sender):
    response = client.post(BASE_URL, json=payload_sem_sender)
    assert response.status_code == 200
    assert response.json()["status"] == "no_sender"


def test_payload_invalido(payload_invalido):
    response = client.post(BASE_URL, json=payload_invalido)
    assert response.status_code == 200
    assert "status" in response.json()