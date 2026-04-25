from backend.database import SessionLocal, engine, settings, Base
from backend.models import Usuario
from backend.auth import pwd_context
import sys
import os
import getpass

# Adiciona o diretório raiz ao path antes das importações do projeto
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)


def create_initial_admin():
    print("=== Central Transfers - Cadastro de Administrador ===")
    print(f"DEBUG: Conectando em -> {settings.full_database_url}\n")

    # Garante que as tabelas estejam criadas (útil para o primeiro run)
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        email = input("Digite o E-mail do administrador: ")

        user_exists = db.query(Usuario).filter(
            Usuario.email == email).first()
        if user_exists:
            print(f"Erro: O usuário '{email}' já existe.")
            return

        password = getpass.getpass("Senha: ")
        role = "admin"

        hashed_pwd = pwd_context.hash(password)
        new_user = Usuario(email=email, senha=hashed_pwd, role=role)

        db.add(new_user)
        db.commit()
        print(f"\nUsuário '{email}' criado com sucesso como ADMIN!")
    except Exception as e:
        db.rollback()
        print(f"\nErro ao criar usuário: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    create_initial_admin()
