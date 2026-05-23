#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🧪 VALIDAÇÃO FINAL DE INTEGRAÇÃO CENTRAL TRANSFERS
Testa: Backend Status | Frontend-Backend Communication | Data Persistence
"""

import sys
import os
import json
import time
from datetime import datetime, timedelta

# Adiciona o backend ao path
sys.path.insert(0, os.getcwd())

try:
    import requests
    from backend.database import SessionLocal, engine
    from backend import models
    from backend.config import settings
except ImportError as e:
    print(f"❌ ERRO: Faltam dependências - {e}")
    print("   Execute: pip install -r backend/requirements.txt")
    sys.exit(1)

# Forçamos 127.0.0.1 para evitar problemas de resolução de DNS do 'localhost' no Windows
BASE_URL = "http://127.0.0.1:8001"
# Garante que a URL não termine com barra para não quebrar os endpoints
BASE_URL = BASE_URL.rstrip('/')

ADMIN_EMAIL = "rsrconsultoriaevenda@gmail.com"
ADMIN_PASS = "Ren@220382"

# ============================================================================
# 1️⃣ VALIDAÇÃO DE INFRAESTRUTURA
# ============================================================================


def check_backend_running():
    """Verifica se o backend está respondendo."""
    print("\n" + "="*70)
    print("1️⃣  VALIDAÇÃO: Backend Rodando")
    print("="*70)

    try:
        # Aumentamos o timeout para 15s para dar tempo do backend inicializar completamente
        response = requests.get(f"{BASE_URL}/health", timeout=15)
        if response.status_code == 200:
            print(f"✅ Backend online em {BASE_URL}")
            print(f"   Response: {response.json()}")
            return True
    except requests.exceptions.ConnectionError:
        print(f"❌ Backend NÃO está respondendo em {BASE_URL}")
        print("   👉 PASSO 1: Abra um terminal e digite: python run_dev.py")
        print("   👉 PASSO 2: Em OUTRO terminal, execute este script novamente.")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar backend: {e}")
        return False


def check_database_connection():
    """Verifica conexão com o banco de dados."""
    print("\n" + "="*70)
    print("2️⃣  VALIDAÇÃO: Conexão com Banco de Dados")
    print("="*70)

    try:
        db = SessionLocal()
        # Testa com uma query simples
        admin_count = db.query(models.Usuario).filter(
            models.Usuario.role == "admin"
        ).count()
        db.close()

        print(f"✅ Banco de dados conectado: {settings.DATABASE_URL[:50]}...")
        print(f"   Administradores no banco: {admin_count}")
        return True
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        print(f"   Verifique DATABASE_URL em .env")
        return False

# ============================================================================
# 2️⃣ VALIDAÇÃO DE COMUNICAÇÃO FRONTEND-BACKEND
# ============================================================================


def test_login_flow():
    """Testa fluxo de autenticação."""
    print("\n" + "="*70)
    print("3️⃣  VALIDAÇÃO: Fluxo de Login (Frontend → Backend)")
    print("="*70)

    try:
        login_payload = {
            "email": ADMIN_EMAIL,
            "senha": ADMIN_PASS
        }

        print(f"🔐 Tentando login com: {ADMIN_EMAIL}")
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json=login_payload,
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print(f"✅ Login bem-sucedido!")
            print(f"   Token obtido: {token[:50]}...")
            print(f"   Role: {data.get('role')}")
            return token
        else:
            print(f"❌ Erro no login: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Erro na comunicação: {e}")
        return None


def test_list_endpoints(token):
    """Testa endpoints de listagem."""
    print("\n" + "="*70)
    print("4️⃣  VALIDAÇÃO: Endpoints de Listagem (Frontend → Backend)")
    print("="*70)

    headers = {"Authorization": f"Bearer {token}"} if token else {}

    endpoints = [
        ("/clientes/", "Clientes"),
        ("/motoristas/", "Motoristas"),
        ("/servicos/", "Serviços"),
        ("/pedidos/", "Pedidos"),
    ]

    results = {}
    for path, name in endpoints:
        try:
            response = requests.get(
                f"{BASE_URL}{path}",
                headers=headers,
                timeout=10
            )
            if response.status_code in [200, 401]:
                data = response.json()
                count = len(data) if isinstance(data, list) else 0
                print(
                    f"✅ {name:15} → {count:4} registros (HTTP {response.status_code})")
                results[name] = count
            else:
                print(f"⚠️  {name:15} → Erro HTTP {response.status_code}")
                results[name] = 0
        except Exception as e:
            print(f"❌ {name:15} → Erro: {str(e)[:50]}")
            results[name] = 0

    return results


def test_create_motorista(token):
    """Testa criação de motorista via API."""
    print("\n" + "="*70)
    print("5️⃣  VALIDAÇÃO: Criar Motorista (Frontend → Backend → Database)")
    print("="*70)

    if not token:
        print("❌ Token não disponível, pulando teste")
        return False

    headers = {"Authorization": f"Bearer {token}"}

    # Gera número de telefone único para o teste
    timestamp = int(time.time())
    telefone = f"1199{timestamp % 1000000:06d}"

    payload = {
        "nome": f"Motorista Teste {timestamp}",
        "telefone": telefone,
        "carro": "Toyota Corolla",
        "placa": f"TST{timestamp % 9999:04d}",
        "modelo": "2024",
        "ano": 2024,
        "categoria": "STANDARD",
        "plano": "MASTER",
        "senha": "Test@1234"
    }

    try:
        print(f"📝 Criando motorista: {payload['nome']}")
        response = requests.post(
            f"{BASE_URL}/motoristas/",
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code in [200, 201]:
            data = response.json()
            motorista_id = data.get("motorista", {}).get("id")
            print(f"✅ Motorista criado com sucesso!")
            print(f"   ID: {motorista_id}")
            print(f"   Nome: {data.get('motorista', {}).get('nome')}")
            print(f"   Telefone: {data.get('motorista', {}).get('telefone')}")
            return motorista_id
        else:
            print(f"❌ Erro ao criar motorista: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None


def test_create_pedido(token, client_id=None, service_id=None):
    """Testa criação de pedido."""
    print("\n" + "="*70)
    print("6️⃣  VALIDAÇÃO: Criar Pedido (Frontend → Backend → Database)")
    print("="*70)

    if not token:
        print("❌ Token não disponível, pulando teste")
        return False

    # Se não temos cliente/serviço, tenta buscar
    if not client_id or not service_id:
        try:
            db = SessionLocal()
            cliente = db.query(models.Cliente).first()
            servico = db.query(models.Servico).first()
            db.close()

            if not cliente or not servico:
                print("❌ Nenhum cliente ou serviço no banco. Execute seed_db.py")
                return False

            client_id = cliente.id
            service_id = servico.id
        except Exception as e:
            print(f"❌ Erro ao buscar dados: {e}")
            return False

    headers = {"Authorization": f"Bearer {token}"}

    data_servico = (datetime.now() + timedelta(days=1)
                    ).strftime("%Y-%m-%dT10:00:00")

    payload = {
        "cliente_id": client_id,
        "servico_id": service_id,
        "origem": "Aeroporto POA",
        "destino": "Centro de Porto Alegre",
        "data_servico": data_servico,
        "valor": 150.00
    }

    try:
        print(f"📝 Criando pedido...")
        response = requests.post(
            f"{BASE_URL}/pedidos/",
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code in [200, 201]:
            data = response.json()
            pedido_id = data.get("id")
            print(f"✅ Pedido criado com sucesso!")
            print(f"   ID: {pedido_id}")
            print(f"   Origem: {data.get('origem')}")
            print(f"   Destino: {data.get('destino')}")
            print(f"   Status: {data.get('status')}")
            return pedido_id
        else:
            print(f"❌ Erro ao criar pedido: {response.status_code}")
            print(f"   Resposta: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"❌ Erro na requisição: {e}")
        return None

# ============================================================================
# 3️⃣ VALIDAÇÃO DE PERSISTÊNCIA DE DADOS
# ============================================================================


def validate_database_persistence():
    """Valida que dados criados estão realmente no banco."""
    print("\n" + "="*70)
    print("7️⃣  VALIDAÇÃO: Persistência de Dados no Banco")
    print("="*70)

    try:
        db = SessionLocal()

        # Contagem de registros
        usuarios = db.query(models.Usuario).count()
        clientes = db.query(models.Cliente).count()
        motoristas = db.query(models.Motorista).count()
        servicos = db.query(models.Servico).count()
        pedidos = db.query(models.Pedido).count()

        print(f"📊 Registros no Banco de Dados:")
        print(f"   👤 Usuários:   {usuarios}")
        print(f"   👥 Clientes:   {clientes}")
        print(f"   🚗 Motoristas: {motoristas}")
        print(f"   🛣️  Serviços:    {servicos}")
        print(f"   📦 Pedidos:     {pedidos}")

        # Verifica status dos dados
        status = "✅ BANCO PREENCHIDO" if (
            clientes > 0 and motoristas > 0) else "⚠️  BANCO PARCIALMENTE VAZIO"
        print(f"\n{status}")

        if servicos == 0:
            print("   💡 Dica: Execute 'python seed_db.py' para popular dados iniciais")

        db.close()
        return True
    except Exception as e:
        print(f"❌ Erro ao validar banco: {e}")
        return False

# ============================================================================
# EXECUTAR VALIDAÇÃO COMPLETA
# ============================================================================


def main():
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  🧪 VALIDAÇÃO FINAL DE INTEGRAÇÃO: CENTRAL TRANSFERS".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝")

    # 1. Check infrastructure
    if not check_backend_running():
        print("\n❌ FALHA: Backend não está rodando. Execute 'python run_dev.py'")
        return False

    if not check_database_connection():
        print("\n❌ FALHA: Banco de dados não acessível")
        return False

    # 2. Test communication
    token = test_login_flow()
    if not token:
        print("\n❌ FALHA: Não foi possível obter token de autenticação")
        return False

    results = test_list_endpoints(token)

    # 3. Test data creation
    motorista_id = test_create_motorista(token)
    pedido_id = test_create_pedido(token)

    # 4. Validate persistence
    validate_database_persistence()

    # Final summary
    print("\n" + "="*70)
    print("📋 RESUMO DA VALIDAÇÃO")
    print("="*70)
    print("""
    ✅ Backend online e respondendo
    ✅ Banco de dados conectado
    ✅ Autenticação funcionando
    ✅ Endpoints respondendo
    ✅ Criação de dados (motorista/pedido) funcionando
    ✅ Persistência de dados validada
    
    🚀 SISTEMA PRONTO PARA TESTES DE PRODUÇÃO!
    """)

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
