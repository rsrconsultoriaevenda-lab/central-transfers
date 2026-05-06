from backend.database import SessionLocal
from backend.models import Servico, Usuario
from backend.auth import hash_senha

def seed():
    db = SessionLocal()
    print("=== Populando Banco de Dados ===")

    admin_email = "rsrconsultoriaevenda@gmail.com"

    if not db.query(Usuario).filter(Usuario.email == admin_email).first():
        admin = Usuario(
            email=admin_email,
            senha=hash_senha("Ren@220382"),
            role="admin"
        )
        db.add(admin)
        print("Admin criado")

    if db.query(Servico).count() == 0:
        servicos = [
            Servico(nome="Transfer Aeroporto", tipo="TRANSFER", valor=150),
            Servico(nome="City Tour", tipo="PASSEIO", valor=300),
        ]
        db.add_all(servicos)
        print("Serviços criados")

    db.commit()
    db.close()
    print("Seed finalizado")


if __name__ == "__main__":
    seed()