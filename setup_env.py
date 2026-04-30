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

        content = f"""# ==============================================================================
        # 🛠️ CONFIGURAÇÕES DO BACKEND (PYTHON / FASTAPI)
        # ==============================================================================
        APP_NAME=central-transfers
        ENV=development

        # SEGURANÇA
        SECRET_KEY={sk}
        ALGORITHM=HS256
        ACCESS_TOKEN_EXPIRE_MINUTES=60

        # DATABASE (Substitua pelos seus dados reais do Aiven)
        DATABASE_URL=postgresql+psycopg2://user:password@host:port/dbname?sslmode=require

        # MERCADO PAGO
        MERCADO_PAGO_ACCESS_TOKEN=cole_seu_token_aqui
        MERCADO_PAGO_WEBHOOK_SECRET={ws}

        # WHATSAPP (META API)
        WHATSAPP_TOKEN=cole_seu_token_aqui
        WHATSAPP_PHONE_NUMBER_ID=cole_seu_id_aqui
        WHATSAPP_API_VERSION=v20.0
        WHATSAPP_VERIFY_TOKEN={secrets.token_urlsafe(16)}

        # ==============================================================================
        # 🌐 CONFIGURAÇÕES DO FRONTEND (VITE)
        # ==============================================================================
        VITE_API_URL=http://localhost:8000
        VITE_MERCADO_PAGO_PUBLIC_KEY=cole_sua_public_key_aqui
        """

        with open(env_path, "w", encoding="utf-8") as f:
            f.write(content)

            print("✅ Arquivo .env criado com chaves de segurança geradas!")
            print("👉 Agora, abra o arquivo e cole apenas os tokens externos (Meta/Mercado Pago).")

if __name__ == "__main__":
    create_env_file()