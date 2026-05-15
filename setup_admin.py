from backend.database import SessionLocal
from backend.models import Usuario
from backend.auth import hash_senha
from backend.config import settings
import os


def setup_initial_admin():
    """Garante a existência do administrador configurado no .env"""
    db = SessionLocal()
    try:
        # Tenta pegar do config, senão direto do ambiente (evita AttributeError)
        admin_email = getattr(settings, "ADMIN_EMAIL",
                              os.getenv("ADMIN_EMAIL"))
        admin_pass = getattr(settings, "ADMIN_PASS", os.getenv("ADMIN_PASS"))

        if not admin_email or not admin_pass:
            print("❌ ADMIN_EMAIL ou ADMIN_PASS não configurados no ambiente.")
            return

        user = db.query(Usuario).filter(Usuario.email == admin_email).first()

        if not user:
            novo_admin = Usuario(
                email=admin_email,
                senha_hash=hash_senha(admin_pass),
                role="admin"
            )
            db.add(novo_admin)
            db.commit()
            print(f"✅ Administrador {admin_email} criado com sucesso.")
        else:
            print(f"ℹ️ Administrador {admin_email} já existe no banco.")
    except Exception as e:
        print(f"❌ Erro ao inicializar Admin Mestre: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    setup_initial_admin()
