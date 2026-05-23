import os
import subprocess
import sys
from pathlib import Path

# Carrega variáveis de ambiente se o pacote estiver disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Garante que o diretório raiz está no path para importar o backend
sys.path.append(os.getcwd())


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

    # Nota: A verificação de variáveis críticas agora é feita de forma inteligente
    # pelo backend.check_standards (Step 1), que permite a correção imediata.

    # 1. Auditoria de Segurança e Configurações
    try:
        import check_standards as audit
    except ImportError:
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

    # 1.1 Verificação de Conectividade e Integridade
    print("\n🔍 Testando conexão com o Banco de Dados...")

    # 2. Migrações de Banco de Dados (aplicamos antes da checagem de integridade)
    if not run_step("alembic upgrade head", "Atualizando esquema do Banco de Dados (Alembic)"):
        print("\n❌ Erro ao aplicar migrações no Banco de Dados.")
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

    # 3. Verificação de Conectividade e Integridade (após migrações)
    if not run_step(f"{sys.executable} check_system.py", "Verificando integridade do sistema"):
        print("❌ O sistema não está íntegro para registros reais.")
        sys.exit(1)
    # 4. Setup do Admin Mestre
    # Garantir que o subprocess tenha PYTHONPATH apontando para o diretório do projeto
    os.environ.setdefault("PYTHONPATH", os.getcwd())
    if not run_step(f"{sys.executable} setup_admin.py", "Configurando Administrador Mestre"):
        sys.exit(1)

    # 5. Seed opcional
    confirm = input(
        "\n🌱 Deseja popular o banco com dados iniciais (Seed)? (s/N): ")
    if confirm.lower() == 's':
        run_step(f"{sys.executable} seed_db.py", "Populando dados iniciais")

    print("\n" + "═" * 45)
    print("🚀 PROJETO PRONTO PARA PRODUÇÃO!")
    print("═" * 45)


if __name__ == "__main__":
    main()
