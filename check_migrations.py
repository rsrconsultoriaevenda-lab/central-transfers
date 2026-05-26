import subprocess
import sys
import os
from pathlib import Path

# Carrega variáveis de ambiente se o pacote estiver disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def check_alembic_migrations():
    print("\n🔍 Verificando status das migrações do banco de dados...")

    # Determina o caminho para alembic.ini
    alembic_ini_path = Path("backend/alembic.ini")
    alembic_cfg_option = f"-c {alembic_ini_path}" if alembic_ini_path.exists() else ""

    if not alembic_ini_path.exists():
        print("❌ Erro: Arquivo alembic.ini não encontrado em 'backend/'.")
        print("Certifique-se de que o Alembic está configurado corretamente.")
        return False

    try:
        # Obter a revisão atual do banco de dados
        current_revision_cmd = f"alembic {alembic_cfg_option} current"
        current_revision_process = subprocess.run(
            current_revision_cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        current_revision_output = current_revision_process.stdout.strip()

        # Extrai o hash da revisão atual. Pode ser algo como "abcdef123456 (head)" ou "abcdef123456"
        # A saída de 'alembic current' pode ser vazia se não houver migrações aplicadas.
        current_revision = current_revision_output.split(
            ' ')[0] if current_revision_output else "Nenhuma migração aplicada"

        # Obter a revisão 'head' (mais recente)
        head_revision_cmd = f"alembic {alembic_cfg_option} history -r head"
        head_revision_process = subprocess.run(
            head_revision_cmd,
            shell=True,
            check=True,
            capture_output=True,
            text=True
        )
        head_revision_output = head_revision_process.stdout.strip()

        # A saída de 'history -r head' geralmente começa com "Rev: <hash> (head)"
        head_revision_line = head_revision_output.splitlines()[
            0] if head_revision_output else ""
        head_revision = head_revision_line.split(' ')[0].replace(
            'Rev:', '').strip() if head_revision_line else "N/A"

        print(f"   Revisão atual do banco: {current_revision}")
        print(f"   Revisão mais recente (head): {head_revision}")

        if current_revision == head_revision:
            print("✅ O banco de dados está com todas as migrações aplicadas (HEAD).")
            return True
        else:
            print("⚠️ O banco de dados NÃO está na revisão mais recente (HEAD).")
            print(
                f"   Execute 'alembic {alembic_cfg_option} upgrade head' para aplicar as migrações pendentes.")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar comando Alembic: {e}")
        print(f"   Stdout: {e.stdout}")
        print(f"   Stderr: {e.stderr}")
        print("   Verifique se o Alembic está instalado, configurado corretamente e se a DATABASE_URL está acessível.")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


if __name__ == "__main__":
    # Garante que o diretório raiz está no path para importar o backend se necessário
    sys.path.append(os.getcwd())
    check_alembic_migrations()
