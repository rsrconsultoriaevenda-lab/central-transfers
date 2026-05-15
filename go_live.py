import os
import subprocess
import sys
from pathlib import Path

REQUIRED_ENV_VARS = ["DATABASE_URL", "MERCADO_PAGO_ACCESS_TOKEN", "SECRET_KEY", "FRONTEND_URL"]

def run_step(command, description):
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Falha em: {description}")
        return False


def update_env_variable(key, value):
    """Atualiza ou adiciona uma variável no arquivo .env"""
    env_path = Path(".env")
    if not env_path.exists():
        return False

    lines = env_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    found = False

    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


def main():
    print("🏗️  PREPARANDO LANÇAMENTO CENTRAL TRANSFERS")
    print("=" * 45)

    # 0. Verificação de Variáveis Críticas
    print("📋 Verificando variáveis de ambiente essenciais...")
    for var in REQUIRED_ENV_VARS:
        if not os.getenv(var):
            print(f"❌ ERRO: A variável {var} não está definida no ambiente.")
            sys.exit(1)
    print("✅ Variáveis críticas encontradas.")

    # 1. Auditoria de Segurança
    import backend.check_standards as audit
    success, missing_keys = audit.run_audit()

    if not success:
        print("\n🛠️  Detectamos pendências na configuração.")
        for key in missing_keys:
            print(f"\n⚠️  A variável {key} está ausente ou com valor padrão.")
            val = input(f"👉 Cole aqui o VALOR para {key}: ").strip()
            if val:
                update_env_variable(key, val)
        print("\n✅ Arquivo .env atualizado com sucesso!")
        print(
            "🔄 Por favor, execute 'python go_live.py' novamente para validar e prosseguir.")
        sys.exit(0)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Importe suas configurações (onde provavelmente está o ALLOWED_ORIGINS)
from backend.config import settings 

app = FastAPI(title="Central Transfers API")

# 1. Definição das origens permitidas
# Você pode usar a lista do seu arquivo de configuração ou definir manualmente:
origins = [
    "http://localhost:5173",    # Frontend Cliente (Vite)
    "http://localhost:5174",    # Painel SaaS / Driver
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "https://central-transfers.vercel.app",
]

# Adiciona dinamicamente a URL do ambiente se definida
env_frontend = os.getenv("FRONTEND_URL")
if env_frontend and env_frontend not in origins:
    origins.append(env_frontend.rstrip("/"))

# origins = settings.ALLOWED_ORIGINS

# 2. Adição do Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Lista de domínios que podem acessar a API
    allow_credentials=True,     # Permite envio de cookies/auth headers
    allow_methods=["*"],        # Permite todos os métodos (GET, POST, PUT, DELETE, etc)
    allow_headers=["*"],        # Permite todos os headers
)

# 3. Agora sim, seus endpoints e WebSockets
@app.get("/")
async def root():
    return {"status": "online"}

@app.websocket("/ws/{motorista_id}")
async def websocket_endpoint(websocket: WebSocket, motorista_id: int):
    # Sua lógica de WebSocket aqui...
    pass
    # 1.1 Verificação de Conectividade com o Banco
    print("\n🔍 Testando conexão com o Banco de Dados...")
    if not run_step(f"{sys.executable} check_system.py", "Verificando integridade do sistema"):
        print("❌ O sistema não está íntegro para registros reais.")
        sys.exit(1)

    # 2. Migrações de Banco de Dados
    if not run_step("alembic upgrade head", "Atualizando esquema do Banco de Dados (Alembic)"):
        print("\n❌ Erro de conexão ou autenticação com o Banco de Dados.")
        print("DICA: Verifique se o usuário/senha no DATABASE_URL estão corretos.")
        retry = input("Deseja atualizar a DATABASE_URL agora? (s/N): ").lower()
        if retry == 's':
            new_url = input("👉 Cole a nova DATABASE_URL: ").strip()
            if new_url:
                update_env_variable("DATABASE_URL", new_url)
                print("✅ URL atualizada. Execute o script novamente para validar.")
                sys.exit(0)
        else:
            sys.exit(1)

    # 3. Setup do Admin Mestre
    if not run_step(f"{sys.executable} -m backend.setup_admin", "Configurando Administrador Mestre"):
        sys.exit(1)

    # 4. Seed opcional
    confirm = input(
        "\n🌱 Deseja popular o banco com dados iniciais (Seed)? (s/N): ")
    if confirm.lower() == 's':
        run_step(f"{sys.executable} seed_db.py", "Populando dados iniciais")

    print("\n" + "═" * 45)
    print("🚀 PROJETO PRONTO PARA PRODUÇÃO!")
    print("═" * 45)


if __name__ == "__main__":
    main()
