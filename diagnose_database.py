#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🔍 DIAGNÓSTICO DO SISTEMA - Central Transfers
Valida estado do banco de dados, backend e comunicação
"""

from backend.config import settings
from backend import models
from backend.database import SessionLocal
import sys
import os
import requests
from sqlalchemy import text

sys.path.insert(0, os.getcwd())


def diagnose():
    """Executa diagnóstico completo do sistema."""

    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + "  🔍 DIAGNÓSTICO DO SISTEMA: CENTRAL TRANSFERS".center(68) + "║")
    print("╚" + "="*68 + "╝\n")

    # 1. Database URL
    print("1️⃣  CONFIGURAÇÃO DO BANCO DE DADOS")
    print("-" * 70)
    db_url = settings.DATABASE_URL
    if "postgresql" in db_url:
        print(f"✅ PostgreSQL detectado")
        db_type = "PostgreSQL (Aiven)"
    elif "mysql" in db_url:
        print(f"✅ MySQL detectado")
        db_type = "MySQL"
    elif "sqlite" in db_url:
        print(f"⚠️  SQLite detectado (Desenvolvimento)")
        db_type = "SQLite"
    else:
        print(f"❓ Tipo desconhecido")
        db_type = "Desconhecido"

    # Mascarar credenciais
    masked_url = db_url.replace(db_url.split(
        "@")[0] if "@" in db_url else "", "[CREDENCIAIS]")
    print(f"   URL: {masked_url}\n")

    # 2. Database Connection
    print("2️⃣  CONEXÃO COM O BANCO")
    print("-" * 70)
    try:
        db = SessionLocal()
        # Test connection
        result = db.execute(text("SELECT 1"))
        print(f"✅ Conexão bem-sucedida com {db_type}\n")
    except Exception as e:
        print(f"❌ Erro na conexão: {e}\n")
        return False

    # 3. Database Structure
    print("3️⃣  ESTRUTURA DO BANCO")
    print("-" * 70)

    tables = [
        ("Usuario", models.Usuario),
        ("Motorista", models.Motorista),
        ("Cliente", models.Cliente),
        ("Pedido", models.Pedido),
        ("Servico", models.Servico),
        ("Mensalidade", models.Mensalidade),
    ]

    for table_name, model_class in tables:
        try:
            count = db.query(model_class).count()
            print(f"   ✅ {table_name:15} → {count:6} registros")
        except Exception as e:
            print(f"   ❌ {table_name:15} → Erro: {str(e)[:40]}")

    print()

    # 4. User Analysis
    print("4️⃣  ANÁLISE DE USUÁRIOS")
    print("-" * 70)

    usuarios = db.query(models.Usuario).all()
    if not usuarios:
        print("   ⚠️  Nenhum usuário no banco")
    else:
        for u in usuarios:
            role_icon = "👤" if u.role == "admin" else "🚗"
            print(f"   {role_icon} {u.email:40} → Role: {u.role}")
    print()

    # 5. Motorista Analysis
    print("5️⃣  ANÁLISE DE MOTORISTAS")
    print("-" * 70)

    motoristas = db.query(models.Motorista).all()
    if not motoristas:
        print("   ⚠️  Nenhum motorista no banco")
    else:
        for m in motoristas[:5]:  # Mostrar apenas os 5 primeiros
            status_icon = "🟢" if m.status == "ATIVO" else "🔴"
            print(
                f"   {status_icon} {m.nome:25} | Tel: {m.telefone:15} | Plano: {m.plano}")
        if len(motoristas) > 5:
            print(f"   ... e {len(motoristas) - 5} motoristas mais")
    print()

    # 6. Pedido Analysis
    print("6️⃣  ANÁLISE DE PEDIDOS")
    print("-" * 70)

    pedidos = db.query(models.Pedido).all()
    if not pedidos:
        print("   ⚠️  Nenhum pedido no banco")
    else:
        print(f"   📦 Total de pedidos: {len(pedidos)}")

        # Contar por status
        from sqlalchemy import func
        status_counts = db.query(
            models.Pedido.status,
            func.count(models.Pedido.id).label("count")
        ).group_by(models.Pedido.status).all()

        for status, count in status_counts:
            status_icon = {
                "PENDENTE": "⏳",
                "PAGO": "💳",
                "ACEITO": "✅",
                "CONCLUIDO": "🏁",
                "CANCELADO": "❌"
            }.get(status, "❓")
            print(f"   {status_icon} {status:12} → {count} pedidos")
    print()

    # 7. Seviços
    print("7️⃣  SERVIÇOS CADASTRADOS")
    print("-" * 70)

    servicos = db.query(models.Servico).all()
    if not servicos:
        print("   ⚠️  Nenhum serviço cadastrado")
        print("   💡 Dica: Execute 'python seed_db.py' para popular dados iniciais")
    else:
        for s in servicos[:5]:
            print(f"   🛣️  {s.nome:30} → R$ {s.valor:8.2f}")
        if len(servicos) > 5:
            print(f"   ... e {len(servicos) - 5} serviços mais")
    print()

    # 7.1. Integration Analysis
    print("7️⃣.1️⃣  ANÁLISE DE INTEGRAÇÕES")
    print("-" * 70)
    mp_token = settings.MERCADO_PAGO_ACCESS_TOKEN
    if not mp_token:
        print("   ❌ Mercado Pago: Token não configurado no .env/Render")
    else:
        print(f"   ✅ Mercado Pago: Token detectado ({mp_token[:10]}...)")
        try:
            resp = requests.get(
                "https://api.mercadopago.com/v1/me",
                headers={"Authorization": f"Bearer {mp_token}"},
                timeout=5
            )
            if resp.status_code == 200:
                print("      🟢 Autenticação na API do Mercado Pago: OK")
            else:
                print(f"      🔴 Erro na API do Mercado Pago: {resp.status_code} - {resp.text}")
        except Exception as e:
            print(f"      ⚠️ Falha ao conectar no Mercado Pago: {e}")
    print()

    # 8. Summary
    print("8️⃣  RESUMO DO BANCO")
    print("-" * 70)

    total_users = db.query(models.Usuario).count()
    total_motoristas = db.query(models.Motorista).count()
    total_clientes = db.query(models.Cliente).count()
    total_pedidos = db.query(models.Pedido).count()
    total_servicos = db.query(models.Servico).count()

    print(f"""
    Registros Totais:
    ├─ 👤 Usuários:     {total_users:4}
    ├─ 🚗 Motoristas:   {total_motoristas:4}
    ├─ 👥 Clientes:     {total_clientes:4}
    ├─ 📦 Pedidos:      {total_pedidos:4}
    └─ 🛣️  Serviços:     {total_servicos:4}
    """)

    # Status Geral
    status_icon = "🟢" if (total_users > 0 and total_servicos > 0) else "🟡"
    print(f"   {status_icon} Status Geral: {'Banco com dados' if total_users > 0 else 'Banco vazio - execute seed'}\n")

    db.close()
    return True


if __name__ == "__main__":
    try:
        diagnose()
    except Exception as e:
        print(f"\n❌ Erro durante diagnóstico: {e}")
        sys.exit(1)
