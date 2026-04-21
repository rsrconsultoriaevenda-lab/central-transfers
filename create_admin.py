from backend.auth import pwd_context
from backend.models import Usuario, Base
from backend.database import SessionLocal, engine
import sys
import os
import getpass

# Adiciona o diretório raiz ao path para que o Python encontre o módulo 'backend'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def create_initial_admin():
    print("=== Central Transfers - Cadastro de Administrador ===")

    # Garante que as tabelas estejam criadas (útil para o primeiro run)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        username = input("Nome de usuário: ")

        user_exists = db.query(Usuario).filter(
            Usuario.username == username).first()
        if user_exists:
            print(f"Erro: O usuário '{username}' já existe.")
            return

        password = getpass.getpass("Senha: ")

        hashed_pwd = pwd_context.hash(password)
        new_user = Usuario(username=username, hashed_password=hashed_pwd)

        db.add(new_user)
        db.commit()
        print(
            f"\nUsuário '{username}' criado com sucesso! Agora você pode fazer login no painel.")
    except Exception as e:
        db.rollback()
        print(f"\nErro ao criar usuário: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_admin()
