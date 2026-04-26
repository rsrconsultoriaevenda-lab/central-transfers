from backend.config import settings
import os


def testar_configuracoes():
    print("\n=== Diagnóstico de Variáveis de Ambiente ===\n")

    # Verifica a origem da URL do banco
    if settings.DATABASE_URL:
        print(
            f"[DATABASE] DATABASE_URL detectada: {settings.DATABASE_URL[:20]}...")
    else:
        print("[DATABASE] DATABASE_URL não definida, usando fallback local.")
        print(f"    Host: {settings.DB_HOST}")
        print(f"    Porta: {settings.DB_PORT}")

    print(
        f"[DATABASE] URL Final Computada: {settings.database_url[:30]}...")

    print(
        f"\n[WHATSAPP] Token: {'✅ Configurado' if settings.WHATSAPP_TOKEN else '❌ Vazio'}")
    print(f"[WHATSAPP] Verify Token: {settings.WHATSAPP_VERIFY_TOKEN}")
    print(f"[CORS] Origins: {settings.ALLOWED_ORIGINS}")


if __name__ == "__main__":
    testar_configuracoes()
