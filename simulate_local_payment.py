from backend import models
from backend.services.payment_service import PaymentService
from backend.database import SessionLocal
import asyncio
import sys
import os
from unittest.mock import MagicMock, patch

# Adiciona o diretório raiz ao path para importações do backend
sys.path.append(os.getcwd())


async def test_simular_pagamento(choice: str):
    """
    Simula o fluxo completo de aprovação de pagamento ignorando a chamada real ao Mercado Pago.
    """
    db = SessionLocal()

    # Auto-detecção de registro para teste
    if choice == "2":  # Pedido
        target = db.query(models.Pedido).filter(
            models.Pedido.status == models.StatusPedido.PENDENTE).first()
        if not target:
            print("❌ Nenhum Pedido PENDENTE encontrado no banco para testar.")
            return
        external_reference = f"PEDIDO_{target.id}"
    else:  # Mensalidade
        target = db.query(models.Mensalidade).first()
        if not target:
            print("❌ Nenhuma Mensalidade encontrada no banco para testar.")
            return
        external_reference = f"MENSAL_{target.id}"

    print(f"\n🧪 Iniciando simulação para: {external_reference}")
    service = PaymentService()

    # 1. Criamos um Mock para a resposta do Mercado Pago
    # Isso simula o que a API do MP retornaria se consultássemos um ID de pagamento aprovado
    mock_response = {
        "status": "approved",
        "status_detail": "accredited",
        "external_reference": external_reference,
        "id": "999999999",
        "transaction_amount": 150.00
    }

    # 2. Aplicamos o Patch no método get_payment_details para retornar nosso mock
    with patch.object(service, 'get_payment_details', return_value=mock_response):
        try:
            print("🔗 Mock da API ativado. Processando atualização no banco...")

            # Chamamos o método que contém a sua lógica de negócio
            # Passamos um ID fictício '999999999'
            sucesso = await service.process_payment_update("MOCK_PAYMENT_ID", db)

            if sucesso:
                print("✅ Lógica executada com sucesso!")
                # Verifica no banco se a alteração persistiu
                if "MENSAL_" in external_reference:
                    mid = int(external_reference.replace("MENSAL_", ""))
                    m = db.query(models.Mensalidade).get(mid)
                    print(
                        f"   📊 Status no Banco (Mensalidade {mid}): {m.status}")
                elif "PEDIDO_" in external_reference:
                    p = db.query(models.Pedido).get(
                        int(external_reference.replace("PEDIDO_", "")))
                    print(f"   📊 Status Final no Banco: {p.status}")
            else:
                print(
                    f"⚠️  A lógica retornou False. O registro {external_reference} pode já estar PAGO ou o status é incompatível.")

        except Exception as e:
            print(f"❌ Erro durante a simulação: {e}")
        finally:
            db.close()

if __name__ == "__main__":
    # Instruções de uso:
    # Certifique-se de ter um registro no banco (ex: Mensalidade ID 1 ou Pedido ID 1)
    # Execute: python simulate_local_payment.py

    print("🚀 Simulador de Pagamentos Central Transfers")
    print("Escolha o que testar:")
    print("1. Mensalidade (MENSAL_1)")
    print("2. Pedido (PEDIDO_1)")

    opcao = input("\nDigite a opção (1 ou 2): ")

    asyncio.run(test_simular_pagamento(opcao))
