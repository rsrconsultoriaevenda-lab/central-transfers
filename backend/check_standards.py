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
        "MERCADO_PAGO_ACCESS_TOKEN": settings.MERCADO_PAGO_ACCESS_TOKEN,
        "SECRET_KEY": getattr(settings, 'SECRET_KEY', None),
        "VAPID_PRIVATE_KEY": getattr(settings, 'VAPID_PRIVATE_KEY', None),
        "VAPID_PUBLIC_KEY": getattr(settings, 'VAPID_PUBLIC_KEY', None),
        "SMTP_USER": getattr(settings, 'SMTP_USER', None),
        "SMTP_PASS": getattr(settings, 'SMTP_PASS', None),
    }

    for key, value in checks.items():
        if not value or any(x in str(value) for x in ["cole_seu", "SEU_SEGREDO", "temporaria"]):
            print(f"❌ ERRO: {key} não configurado corretamente no .env")
            errors += 1
            failed_keys.append(key)
        else:
            print(f"✅ {key}: OK")

    # 2. Verificações Opcionais / Informativas (Fora do loop principal)
    whatsapp_token = getattr(settings, 'EVOLUTION_API_KEY', None) or getattr(
        settings, 'WHATSAPP_TOKEN', None)
    if not whatsapp_token:
        print(
            "ℹ️  INFO: WhatsApp não configurado (EVOLUTION_API_KEY/WHATSAPP_TOKEN ausente).")
    else:
        print("✅ WHATSAPP: OK")

    sentry = getattr(settings, 'SENTRY_DSN', None)
    if not sentry:
        print("⚠️ AVISO: SENTRY_DSN não configurado. Monitoramento de logs desativado.")

    validation_mode = getattr(settings, 'VALIDATION_MODE', False)
    if validation_mode:
        print("⚠️ AVISO: VALIDATION_MODE está ativo. Desative para Produção!")
        errors += 1

    if errors > 0:
        print(
            f"\n🛑 Auditoria falhou com {errors} erros. O lançamento não é seguro.")
        return False, failed_keys

    print("\n🚀 TUDO PRONTO PARA O GO-LIVE! O sistema está estável.")
    return True, []


if __name__ == "__main__":
    run_audit()
