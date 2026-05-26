import subprocess
import time
import sys
import os
from pathlib import Path


def sanitize_env_file():
    """Remove linhas malformadas do .env para limpar os logs de inicialização."""
    # Verifica tanto na raiz quanto dentro da pasta backend
    for env_loc in [".env", "backend/.env"]:
        env_path = Path(env_loc)
        if env_path.exists():
            try:
                lines = env_path.read_text(encoding="utf-8").splitlines()
                cleaned = [l.strip() for l in lines if "=" in l or l.strip(
                ).startswith("#") or not l.strip()]
                env_path.write_text("\n".join(cleaned) +
                                    "\n", encoding="utf-8")
            except Exception:
                pass


def start_services():
    print("🚀 Iniciando Central Transfers (Ambiente de Desenvolvimento)...")

    # Verificação de Segurança
    sanitize_env_file()
    if not os.path.exists(".env") and not os.path.exists("backend/.env"):
        print("⚠️ AVISO: Arquivo .env não encontrado! O backend pode falhar ao conectar ao banco ou WhatsApp.")
        time.sleep(1)

    # 1. Backend (8001)
    print("📦 [1/3] Iniciando Backend FastAPI...")
    backend = subprocess.Popen(
        [
            sys.executable, "-m", "uvicorn", "backend.main:app",
            "--reload",
            "--reload-exclude", "*.db",
            "--reload-exclude", "*.log",
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

    port_frontend = "5173" if frontend else "---"
    # Vite pula porta se 5173 estiver ocupada
    port_painel = "5174" if frontend else "5173"

    print("\n" + "="*50)
    print("✅ SERVIÇOS INICIALIZADOS")
    print(f"🔗 Backend API:   http://127.0.0.1:8001/docs")
    print(f"🔗 Painel/App:    http://localhost:{port_painel}")
    print("="*50)
    print("\n💡 DICA: Mantenha esta janela aberta e use OUTRO terminal para rodar os testes.")

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
