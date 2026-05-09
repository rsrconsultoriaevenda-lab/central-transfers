import os
import secrets
from pathlib import Path

def generate_secure_keys():
    """Gera chaves aleatórias seguras para o ambiente."""
    print("🔐 Gerando novas chaves de segurança...")
    secret_key = secrets.token_hex(32)
    webhook_secret = secrets.token_hex(20)
    return secret_key, webhook_secret

def create_env_file():
    env_path = Path(".env")

    if env_path.exists():
        print("⚠️ Arquivo .env já existe. Deseja sobrescrever? (s/n)")
        confirm = input().lower()
        if confirm != 's':
            print("Operação cancelada.")
            return

        # Gera chaves automáticas para você não precisar inventar
        sk, ws = generate_secure_keys()

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
            f"# DATABASE (Substitua pelos seus dados reais)\n"
            f"DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname?sslmode=require\n\n"
            f"# MERCADO PAGO\n"
            f"MERCADO_PAGO_ACCESS_TOKEN=cole_seu_token_aqui\n"
            f"MERCADO_PAGO_WEBHOOK_SECRET={ws}\n\n"
            f"# WHATSAPP (META API)\n"
            f"WHATSAPP_TOKEN=cole_seu_token_aqui\n"
            f"WHATSAPP_PHONE_NUMBER_ID=cole_seu_id_aqui\n"
            f"WHATSAPP_API_VERSION=v20.0\n"
            f"WHATSAPP_VERIFY_TOKEN={secrets.token_urlsafe(16)}\n\n"
            f"# ==============================================================================\n"
            f"# 🌐 CONFIGURAÇÕES DO FRONTEND (VITE)\n"
            f"# ==============================================================================\n"
            f"VITE_API_URL=http://localhost:8001\n"
            f"VITE_MERCADO_PAGO_PUBLIC_KEY=cole_sua_public_key_aqui\n"
        )

        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)

            print("✅ Arquivo .env criado com chaves de segurança geradas!")
            print("👉 Agora, abra o arquivo e cole apenas os tokens externos (Meta/Mercado Pago).")

if __name__ == "__main__":
    create_env_file()