from backend.database import SessionLocal, engine, Base
from backend.models import Servico, Usuario, Cliente, Motorista
from backend.auth import hash_senha
from decimal import Decimal
import os


def seed():
    # Proteção para não rodar em produção sem intenção
    if os.getenv("ENV") == "production":
        confirm = input(
            "⚠️ ATENÇÃO: Detectado ambiente de PRODUÇÃO. Deseja realmente rodar o seed? (s/N): ")
        if confirm.lower() != 's':
            print("Operação cancelada.")
            return

    # Ao usar Alembic, as tabelas devem ser criadas via migrações.
    # Se o banco estiver vazio, rode 'alembic upgrade head' antes do seed.
    # No entanto, mantemos como fallback ou comentamos se preferir automação total.
    # Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    print("=== Populando Banco de Dados ===")

    admin_email = "rsrconsultoriaevenda@gmail.com"
    admin_user = db.query(Usuario).filter(Usuario.email == admin_email).first()

    if not admin_user:
        admin_user = Usuario(email=admin_email, role="admin")
        db.add(admin_user)
        print("Admin criado")
    else:
        admin_user.role = "admin"
        print("Admin atualizado")

    admin_user.senha_hash = hash_senha("Ren@220382")

    if db.query(Servico).count() == 0:
        servicos = [
            Servico(nome="Transfer Aeroporto",
                    tipo="TRANSFER", valor=Decimal("150.00")),
            Servico(nome="City Tour", tipo="PASSEIO", valor=Decimal("300.00")),
            Servico(nome="Transfer Gramado/POA",
                    tipo="TRANSFER", valor=Decimal("280.00")),
        ]
        db.add_all(servicos)
        print("Serviços criados")

    if db.query(Cliente).count() == 0:
        cliente = Cliente(
            nome="Cliente Teste E2E",
            telefone="54999999999",
            email="teste@central.com"
        )
        db.add(cliente)
        print("Cliente de teste criado")

    if db.query(Motorista).count() == 0:
        m1 = Motorista(
            nome="Motorista Teste E2E",
            telefone="11999999999",
            email="11999999999@motorista.com",
            senha_hash=hash_senha("Ren@220382"),
            carro="Sedan Luxo",
            placa="ABC1D23",
            modelo="Corolla",
            ano=2023,
            plano="MASTER",
            comissao_master=Decimal("15.0")
        )

        m2 = Motorista(
            nome="Motorista Plano Mensal",
            telefone="54988887777",
            email="54988887777@motorista.com",
            senha_hash=hash_senha("Ren@220382"),
            carro="SUV Confort",
            placa="XYZ9G88",
            modelo="SW4",
            ano=2022,
            plano="MENSAL",
            status="ATIVO"
        )

        db.add_all([m1, m2])
        print("Motoristas de teste criados (MASTER e MENSAL)")

    db.commit()
    db.close()
    print("Seed finalizado")


if __name__ == "__main__":
    seed()
