import os
import subprocess
import sys
from pathlib import Path


def sanitize_env_file():
    """Remove linhas malformadas do .env antes de carregar o sistema."""
    env_path = Path(".env")
    if env_path.exists():
        try:
            lines = env_path.read_text(encoding="utf-8").splitlines()
            # Mantém apenas linhas com '=', comentários ou vazias
            cleaned = [l.strip() for l in lines if "=" in l or l.strip(
            ).startswith("#") or not l.strip()]
            env_path.write_text("\n".join(cleaned) + "\n", encoding="utf-8")
        except Exception:
            pass


sanitize_env_file()

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Verificação de versão mínima
if sys.version_info < (3, 10):
    print("❌ Este sistema requer Python 3.10 ou superior.")
    sys.exit(1)

# Garante que o diretório raiz está no path para importar o backend
sys.path.append(os.getcwd())


def run_step(command, description):
    print(f"\n🔄 {description}...")
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Falha em: {description}")
        return False


def update_env_variable(key, value):
    """Atualiza ou adiciona uma variável no arquivo .env"""
    env_path = Path(".env")
    if not env_path.exists():
        env_path.touch()

    content = env_path.read_text(encoding="utf-8")
    lines = content.splitlines()
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
    print("\n🏗️  FINALIZANDO PROJETO CENTRAL TRANSFERS")
    print("=" * 45)

    # 0. Preparação de Ambiente e Assets
    if not os.path.exists(".env"):
        print("📝 Configurando ambiente inicial (.env)...")
        run_step(f"{sys.executable} setup_env.py",
                 "Inicializando variáveis de ambiente")

    if not os.path.exists("logo.png"):
        run_step(f"{sys.executable} make_temp_logo.py",
                 "Gerando logo minimalista padrão")

    run_step(f"{sys.executable} generate_pwa_icons.py",
             "Gerando ícones PWA (192x192, 512x512)")

    # 1. Auditoria de Segurança
    try:
        # Tenta importar o módulo de auditoria local ou do backend
        try:
            import check_standards as audit
        except ImportError:
            import backend.check_standards as audit

        success, missing_keys = audit.run_audit()
        if not success:
            print("\n🛠️  Configurações pendentes detectadas.")
            for key in missing_keys:
                if "VAPID" in key:
                    continue  # VAPID costuma ser auto-gerado no setup_env
                val = input(f"👉 Insira o valor para {key}: ").strip()
                if val:
                    update_env_variable(key, val)
    except Exception:
        print("⚠️  Pulando auditoria detalhada (módulo não encontrado).")

    # 2. Banco de Dados e Migrações
    alembic_cfg = "-c backend/alembic.ini" if os.path.exists(
        "backend/alembic.ini") else ""
    if not run_step(f"alembic {alembic_cfg} upgrade head", "Sincronizando Banco de Dados (Migrations)"):
        print("❌ Verifique sua DATABASE_URL no arquivo .env")
        return False

    # 3. Setup de Usuário e Integridade
    os.environ.setdefault("PYTHONPATH", os.getcwd())
    if os.path.exists("check_system.py"):
        run_step(f"{sys.executable} check_system.py",
                 "Validando integridade do sistema")

    if os.path.exists("setup_admin.py"):
        run_step(f"{sys.executable} setup_admin.py",
                 "Configurando Administrador Mestre")

    # 4. Build de Produção (Frontend)
    confirm_build = input(
        "\n📦 Deseja gerar o build de produção agora? (S/n): ") or 's'
    if confirm_build.lower() == 's' and os.path.exists("painel-saas"):
        if os.path.exists("pwa_finalize.py"):
            run_step(f"{sys.executable} pwa_finalize.py",
                     "Finalizando configurações PWA")

        run_step("npm run build --prefix painel-saas",
                 "Gerando build de produção (Vite)")

    # 5. Seed Opcional
    confirm_seed = input(
        "\n🌱 Deseja popular o banco com dados iniciais (Seed)? (s/N): ")
    if confirm_seed.lower() == 's':
        run_step(f"{sys.executable} seed_db.py", "Populando banco de dados")

    print("\n" + "═" * 45)
    print("🚀 PROJETO FINALIZADO E PRONTO PARA DEPLOY!")
    print("═" * 45)


if __name__ == "__main__":
    main()
