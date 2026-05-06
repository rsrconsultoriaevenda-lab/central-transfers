from backend.database import SessionLocal, engine, Base
from backend import models
from sqlalchemy import inspect

# 🔥 garante que as tabelas existem
Base.metadata.create_all(bind=engine)

db = SessionLocal()

try:
    # Inspeciona o banco de dados para listar tabelas reais
    inspector = inspect(engine)
    tabelas = inspector.get_table_names()
    
    print("\n🔍 Tabelas encontradas no banco de dados:")
    for tabela in tabelas:
        print(f"  - {tabela}")

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