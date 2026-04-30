from backend.database import SessionLocal, engine, Base
from backend.models import Usuario
from backend.auth import hash_senha

def setup_database():
    db = SessionLocal()
    try:
        print("⏳ Conectando ao Aiven e criando tabelas...")
        Base.metadata.create_all(bind=engine)

        email_admin = "rsrconsultoriaevenda@gmail.com" 
        senha_admin = "Ren@220382"      

        user = db.query(Usuario).filter(Usuario.email == email_admin).first()

        if not user:
            novo_admin = Usuario(
                email=email_admin,
                senha=hash_senha(senha_admin),
                role="admin"
            )
            db.add(novo_admin)
            db.commit()
            print(f"✅ Sucesso! Admin {email_admin} criado.")
        else:
            print(f"ℹ️ O usuário {email_admin} já existe no banco.")

    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()