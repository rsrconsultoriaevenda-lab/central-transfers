import sys
import os
from datetime import datetime


def check_step(name, condition, error_msg):
    if condition:
        print(f"✅ {name}")
        return True
    else:
        print(f"❌ {name} - FALHA: {error_msg}")
        return False


def run_audit():
    # Garante que a raiz do projeto esteja no sys.path para importações
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if root_dir not in sys.path:
        sys.path.append(root_dir)

    print(
        f"=== Auditoria de Padrões: Central Transfers ({datetime.now().strftime('%Y-%m-%d')}) ===\n")

    # 1. Verificação de Ambiente
    has_env = os.path.exists(".env") or os.path.exists("backend/.env")
    check_step("Arquivo .env presente", has_env,
               "Crie um arquivo .env para gerenciar segredos.")

    # 2. Verificação de Dependências
    try:
        import fastapi
        import sqlalchemy
        import psycopg
        import mercadopago
        check_step("Dependências principais instaladas", True, "")
    except ImportError as e:
        check_step("Dependências principais instaladas",
                   False, f"Faltando: {e.name}")

    # 3. Verificação de Configuração
    try:
        from backend.config import settings
        current_url = settings.database_url
        db_ok = "postgresql+psycopg" in current_url
        msg = f"A URL deve usar postgresql+psycopg:// (Atual: {current_url.split('@')[-1]})"
        check_step("Driver de Banco (Psycopg 3)", db_ok, msg)

        sec_ok = settings.SECRET_KEY != "SEU_SEGREDO_SUPER_FORTE"
        check_step("Segurança de Chaves", sec_ok,
                   "SECRET_KEY padrão detectada! Mude no .env.")
    except Exception as e:
        print(f"💥 Erro ao carregar configurações: {e}")

    # 4. Verificação de Consistência de Modelos
    try:
        from backend.models import Pedido
        has_created_at = hasattr(Pedido, 'criado_at')
        check_step("Modelo Pedido atualizado (criado_at)",
                   has_created_at, "Coluna criado_at ausente no modelo.")
    except Exception as e:
        print(f"💥 Erro nos modelos: {e}")

    print("\n--- Resultado Final ---")
    print("Se todos os itens acima estiverem com ✅, seu sistema está seguindo os padrões recomendados para deploy.")


if __name__ == "__main__":
    try:
        run_audit()
    except Exception as e:
        print(f"Erro ao executar auditoria: {e}")
