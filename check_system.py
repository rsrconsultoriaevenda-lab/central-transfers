import sys
import os

# Adiciona o diretório atual ao path
sys.path.append(os.getcwd())


def verify():
    print("🔍 Iniciando Verificação de Integridade...")

    try:
        from backend.database import SessionLocal
        from backend import models, auth
        print("✅ Backend: Estrutura base carregada.")

        from backend.routes import auth, pedidos, motoristas, clientes
        print("✅ Rotas: Todos os módulos de rotas importados sem erros de sintaxe.")

        db = SessionLocal()
        from sqlalchemy import text, inspect
        db.execute(text("SELECT 1"))
        print("✅ Banco de Dados: Conexão estabelecida.")

        # Listagem de tabelas existentes
        inspector = inspect(db.get_bind())
        tables = inspector.get_table_names()
        print(f"📋 Tabelas encontradas ({len(tables)}): {', '.join(tables)}")

        if "usuarios" not in tables:
            print("❌ ERRO: Tabela 'usuarios' não encontrada. As migrações rodaram?")
            sys.exit(1)

        # Verifica se existem motoristas sem senha sem depender do mapeamento completo do modelo
        from sqlalchemy import text
        res = db.execute(text(
            "SELECT count(1) AS cnt FROM motoristas WHERE senha_hash IS NULL")).fetchone()
        try:
            null_pass_drivers = int(res.cnt)
        except Exception:
            null_pass_drivers = int(res[0] or 0)

        if null_pass_drivers > 0:
            print(
                f"⚠️ AVISO: Existem {null_pass_drivers} motoristas sem senha no banco.")
            fix = input(
                "👉 Deseja gerar senhas temporárias ('Mudar123') para eles agora? (s/n): ")
            if fix.lower() == 's':
                temp_hash = auth.hash_senha("Mudar123")
                db.execute(text("UPDATE motoristas SET senha_hash = :h WHERE senha_hash IS NULL"), {
                           "h": temp_hash})
                db.commit()
                print("✅ Senhas corrigidas com sucesso!")
            else:
                print(
                    "💡 DICA: Execute 'UPDATE motoristas SET senha_hash = '...' WHERE senha_hash IS NULL' manualmente.")
                print("         Use `from backend.auth import hash_senha; print(hash_senha('sua_senha_temporaria'))` para gerar o hash.")
        else:
            print("✅ Banco de Dados: Nenhum registro corrompido detectado.")

    except Exception as e:
        print(f"❌ FALHA NA VERIFICAÇÃO: {e}")
        sys.exit(1)

    print("\n🚀 SINAL VERDE: O código está pronto para execução.")


if __name__ == "__main__":
    verify()
