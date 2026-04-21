import subprocess
import time
import sys
import os


def start_services():
    print("🚀 Iniciando Central Transfers (Ambiente de Desenvolvimento)...")

    # 1. Backend (8001)
    print("📦 [1/3] Iniciando Backend FastAPI...")
    backend = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--reload", "--port", "8001"])

    time.sleep(2)  # Aguarda o backend carregar

    # 2. Frontend Cliente (5173)
    print("🌐 [2/3] Iniciando Frontend Cliente...")
    frontend = subprocess.Popen(
        ["npm", "run", "dev"], cwd="frontend", shell=True)

    # 3. Painel SaaS (5174)
    print("📊 [3/3] Iniciando Painel Administrativo...")
    painel = subprocess.Popen(["npm", "run", "dev"],
                              cwd="painel-saas", shell=True)

    print("\n✅ Todos os serviços estão rodando!")
    print("🔗 API: http://127.0.0.1:8001/docs")
    print("🔗 Cliente: http://127.0.0.1:5173")
    print("🔗 Painel: http://127.0.0.1:5174")

    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando todos os processos...")
        backend.terminate()
        frontend.terminate()
        painel.terminate()
        print("👋 Até logo!")


if __name__ == "__main__":
    start_services()
