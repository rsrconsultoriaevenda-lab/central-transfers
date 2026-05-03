from database import SessionLocal
from models import Usuario
from auth import hash_senha


def restaurar_acesso():
    db = SessionLocal()
    email_admin = "rsrconsultoriaevenda@gmail.com"
    nova_senha = hash_senha("Ren@220382")

    usuario = db.query(Usuario).filter(Usuario.email == email_admin).first()

    if usuario:
        usuario.senha = nova_senha
        usuario.role = "admin"
        print(f"✅ Senha do usuário {email_admin} atualizada com sucesso!")
    else:
        novo_admin = Usuario(email=email_admin, senha=nova_senha, role="admin")
        db.add(novo_admin)
        print(f"🚀 Usuário {email_admin} criado como ADMINISTRADOR!")

    db.commit()
    db.close()


if __name__ == "__main__":
    restaurar_acesso()
