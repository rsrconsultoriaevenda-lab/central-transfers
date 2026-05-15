import os
from backend.config import settings


def run_audit():
    """
    Realiza uma auditoria nas variáveis de ambiente críticas.
    Retorna (success, missing_critical)
    """
    print("\n✈️  Iniciando Auditoria Pré-Voo (Go-Live)...")

    critical_vars = [
        "DATABASE_URL",
        "MERCADO_PAGO_ACCESS_TOKEN",
        "SECRET_KEY",
        "VAPID_PRIVATE_KEY",
        "VAPID_PUBLIC_KEY",
        "ADMIN_EMAIL",
        "ADMIN_PASS"
    ]

    optional_vars = [
        "WHATSAPP_TOKEN",
        "SMTP_USER",
        "SMTP_PASS",
        "SENTRY_DSN"
    ]

    missing_critical = []
    # Detecta placeholders comuns
    placeholders = ["cole_seu", "sua_chave",
                    "password", "placeholder", ":port", "/dbname"]

    for var in critical_vars:
        # Busca no settings ou direto no ambiente como fallback
        value = getattr(settings, var, None) or os.getenv(var)

        is_invalid = not value or any(x in str(value).lower()
                                      for x in placeholders)

        if is_invalid:
            print(f"❌ {var}: ERRO (Valor ausente ou padrão detectado)")
            missing_critical.append(var)
        else:
            print(f"✅ {var}: OK")

    for var in optional_vars:
        value = getattr(settings, var, None) or os.getenv(var)
        is_invalid = not value or any(x in str(value).lower()
                                      for x in placeholders)

        if is_invalid:
            if var == "WHATSAPP_TOKEN":
                print(
                    f"ℹ️  INFO: WhatsApp não configurado (EVOLUTION_API_KEY/WHATSAPP_TOKEN ausente).")
            elif var == "SENTRY_DSN":
                print(
                    f"⚠️  AVISO: SENTRY_DSN não configurado. Monitoramento desativado.")
        else:
            print(f"✅ {var}: OK")

    success = len(missing_critical) == 0
    if success:
        print("\n🚀 TUDO PRONTO PARA O GO-LIVE! O sistema está estável.")

    return success, missing_critical
