from backend.database import SessionLocal, engine, Base
from backend import models

# 🔥 garante que as tabelas existem
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    usuarios = db.query(models.Usuario).all()

    print("\n=== USUÁRIOS ===")

    for u in usuarios:
        print({
            "id": u.id,
            "email": u.email,
            "role": u.role
        })

finally:
    db.close()