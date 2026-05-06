from backend.database import SessionLocal
from backend.models import Usuario
from backend.auth import hash_senha


def criar_admin_local():
    """
    Script simples para garantir que o admin de testes exista no banco local.
    Não deve ser uma instância de FastAPI.
    """
    db = SessionLocal()
    try:
        email_admin = "rsrconsultoriaevenda@gmail.com"
        existe = db.query(Usuario).filter(Usuario.email == email_admin).first()

        if not existe:
            admin = Usuario(
                email=email_admin,
                senha=hash_senha("Ren@220382"),
                role="admin"
            )
            db.add(admin)
            db.commit()
            print(f"✅ Admin {email_admin} criado com sucesso.")
    finally:
        db.close()


if __name__ == "__main__":
    criar_admin_local()
