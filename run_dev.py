import subprocess
import time
import sys
import os


def start_services():
    print("🚀 Iniciando Central Transfers (Ambiente de Desenvolvimento)...")

    # 1. Backend (8001)
    print("📦 [1/3] Iniciando Backend FastAPI...")
    backend = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "backend.main:app",
            "--reload",
            "--reload-dir", os.path.abspath("backend"),
            "--host", "127.0.0.1",
            "--port", "8001"
        ],
        env={**os.environ, "PYTHONPATH": os.getcwd()}
    )

    time.sleep(2)  # Aguarda o backend carregar

    # 2. Frontend Cliente (5173)
    frontend = None
    if os.path.exists("frontend"):
        print("🌐 [2/3] Iniciando Frontend Cliente...")
        frontend = subprocess.Popen(
            ["npm", "run", "dev"], cwd="frontend", shell=True)

    # 3. Painel SaaS (5174)
    painel = None
    if os.path.exists("painel-saas"):
        print("📊 [3/3] Iniciando Painel Administrativo...")
        painel = subprocess.Popen(["npm", "run", "dev"],
                                  cwd="painel-saas", shell=True)
    else:
        print("❌ [3/3] Pasta 'painel-saas' não encontrada!")

    print("\n✅ Todos os serviços estão rodando!")
    print("🔗 API Docs: http://localhost:8001/docs")
    print("🔗 Frontend Unificado: http://localhost:5173")

    try:
        backend.wait()
    except KeyboardInterrupt:
        print("\n🛑 Encerrando todos os processos...")
        backend.terminate()
        backend.wait()  # Garante que o processo uvicorn encerrou
        if frontend:
            frontend.terminate()
        if painel:
            painel.terminate()
        print("👋 Até logo!")


if __name__ == "__main__":
    start_services()
