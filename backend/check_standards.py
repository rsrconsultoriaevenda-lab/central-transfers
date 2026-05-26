import os
import sys
import logging
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PreFlight")


def run_audit():
    """Valida se o ambiente de produção está configurado corretamente."""
    print("\n✈️  Iniciando Auditoria Pré-Voo (Go-Live)...")
    errors = 0
    failed_keys = []

    # Chaves obrigatórias para o funcionamento básico
    checks = {
        "MERCADO_PAGO_ACCESS_TOKEN": getattr(settings, 'MERCADO_PAGO_ACCESS_TOKEN', None),
        "MERCADO_PAGO_WEBHOOK_SECRET": getattr(settings, 'MERCADO_PAGO_WEBHOOK_SECRET', None),
        "DATABASE_URL": getattr(settings, 'DATABASE_URL', os.getenv("DATABASE_URL")),
        "SECRET_KEY": getattr(settings, 'SECRET_KEY', None),
        "FRONTEND_URL": getattr(settings, 'FRONTEND_URL', os.getenv("FRONTEND_URL")),
    }

    for key, value in checks.items():
        if not value or any(x in str(value).lower() for x in ["cole_seu", "seu_segredo", "temporaria", "placeholder"]):
            print(f"❌ ERRO: {key} não configurado corretamente no .env")
            errors += 1
            failed_keys.append(key)

        # Validação de HTTPS para Produção
        if key == "FRONTEND_URL" and value and "https://" not in str(value).lower() and "localhost" not in str(value):
            print(
                f"❌ ERRO: {key} deve usar HTTPS para funcionamento do PWA/Service Worker!")
            errors += 1
            failed_keys.append(key)
        else:
            print(f"✅ {key}: OK")

    # Verificações Opcionais
    whatsapp_token = getattr(settings, 'WHATSAPP_TOKEN', None)
    if not whatsapp_token:
        print("ℹ️  INFO: WhatsApp (Meta) não configurado.")
    else:
        print("✅ WHATSAPP: OK")

    if errors > 0:
        print(f"\n🛑 Auditoria falhou com {errors} erros.")
        return False, failed_keys

    print("\n🚀 TUDO PRONTO PARA O GO-LIVE!")
    return True, []


if __name__ == "__main__":
    run_audit()
