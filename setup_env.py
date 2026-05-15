import os
import secrets
from pathlib import Path
try:
    from pywebpush import vapid_utils
except ImportError:
    vapid_utils = None


def generate_secure_keys():
    """Gera chaves aleatórias seguras para o ambiente."""
    print("🔐 Gerando novas chaves de segurança...")
    secret_key = secrets.token_hex(32)
    mp_webhook_secret = secrets.token_hex(20)
    # Gerar uma senha inicial segura para o admin
    admin_initial_password = secrets.token_urlsafe(16)

    v_priv, v_pub = "INSTALE_PYWEBPUSH_PARA_GERAR", "INSTALE_PYWEBPUSH_PARA_GERAR"
    if vapid_utils:
        v_priv = vapid_utils.generate_private_key()
        v_pub = vapid_utils.get_public_key(v_priv)
    else:
        print("⚠️ pywebpush não instalado. Instale com 'pip install pywebpush' para automatizar VAPID.")

    return secret_key, mp_webhook_secret, v_priv, v_pub, admin_initial_password


def create_env_file():
    env_path = Path(".env")

    if env_path.exists():
        print("⚠️ Arquivo .env já existe. Deseja sobrescrever? (s/n)")
        confirm = input().lower()
        if confirm != 's':
            print("Operação cancelada.")
            return

        # Gera chaves automáticas para você não precisar inventar
        sk, mp_ws, v_priv, v_pub, admin_pass = generate_secure_keys()

        content = (
            f"# ==============================================================================\n"
            f"# 🛠️ CONFIGURAÇÕES DO BACKEND (PYTHON / FASTAPI)\n"
            f"# ==============================================================================\n"
            f"APP_NAME=central-transfers\n"
            f"ENV=development\n\n"
            f"# SEGURANÇA\n"
            f"SECRET_KEY={sk}\n"
            f"ALGORITHM=HS256\n"
            f"ACCESS_TOKEN_EXPIRE_MINUTES=60\n\n"
            f"# ADMIN MASTER\n"
            f"ADMIN_EMAIL=admin@centraltransfers.com\n"
            f"ADMIN_PASS={admin_pass}\n\n"
            f"# DATABASE (Substitua pelos seus dados reais)\n"
            f"DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname?sslmode=require\n\n"
            f"# MERCADO PAGO\n"
            f"MERCADO_PAGO_ACCESS_TOKEN=cole_seu_token_aqui\n"
            f"MERCADO_PAGO_WEBHOOK_SECRET={mp_ws}\n\n"
            f"# WHATSAPP (META API)\n"
            f"WHATSAPP_TOKEN=cole_seu_token_aqui\n"
            f"WHATSAPP_PHONE_NUMBER_ID=cole_seu_id_aqui\n"
            f"WHATSAPP_API_VERSION=v20.0\n"
            f"WHATSAPP_VERIFY_TOKEN={secrets.token_urlsafe(16)}\n\n"
            f"# E-MAIL (SMTP)\n"
            f"SMTP_SERVER=smtp.gmail.com\n"
            f"SMTP_PORT=587\n"
            f"SMTP_USER=cole_seu_email_aqui\n"
            f"SMTP_PASS=cole_sua_senha_de_app_aqui\n\n"
            f"# WEB PUSH (VAPID)\n"
            f"VAPID_PRIVATE_KEY={v_priv}\n"
            f"VAPID_PUBLIC_KEY={v_pub}\n\n"
            f"# ==============================================================================\n"
            f"# 🌐 CONFIGURAÇÕES DO FRONTEND (VITE)\n"
            f"# ==============================================================================\n"
            f"VITE_API_URL=http://localhost:8001\n"
            f"VITE_MERCADO_PAGO_PUBLIC_KEY=cole_sua_public_key_aqui\n"
            f"VITE_VAPID_PUBLIC_KEY={v_pub}\n"
        )

        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)

            print("✅ Arquivo .env criado com chaves de segurança geradas!")
            print(
                "👉 Agora, abra o arquivo e cole apenas os tokens externos (Meta/Mercado Pago).")


if __name__ == "__main__":
    create_env_file()
