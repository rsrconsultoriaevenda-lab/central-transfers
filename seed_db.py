from datetime import datetime

from backend.database import SessionLocal, engine, Base
from backend.models import (
    Servico,
    Usuario,
    Cliente,
    Motorista
)
from backend.auth import hash_senha


def seed():
    db = SessionLocal()

    try:
        print("=== Populando Banco de Dados ===")

        # cria tabelas automaticamente
        Base.metadata.create_all(bind=engine)

        admin_email = "rsrconsultoriaevenda@gmail.com"

        # ADMIN
        admin = db.query(Usuario).filter(
            Usuario.email == admin_email
        ).first()

        if not admin:
            admin = Usuario(
                email=admin_email,
                senha=hash_senha("Ren@220382"),
                role="admin"
            )
            db.add(admin)
            print("✅ Admin criado")

            # SERVIÇOS
            if db.query(Servico).count() == 0:
                servicos = [
                    Servico(
                        nome="Transfer Aeroporto",
                        tipo="TRANSFER",
                        categoria="TRANSFERS",
                        descricao="Transfer aeroporto executivo",
                        capacidade_passageiros=4,
                        capacidade_malas=2,
                        valor=150,
                        valor_padrao=150,
                        ativo=True
                    ),
                    Servico(
                        nome="City Tour",
                        tipo="PASSEIO",
                        categoria="PASSEIOS",
                        descricao="Passeio turístico",
                        capacidade_passageiros=4,
                        capacidade_malas=1,
                        valor=300,
                        valor_padrao=300,
                        ativo=True
                    ),
                ]

                db.add_all(servicos)
                print("✅ Serviços criados")

                # CLIENTE
                if db.query(Cliente).count() == 0:
                    cliente = Cliente(
                        nome="Cliente Teste E2E",
                        email="teste@transfers.com",
                        telefone="5554999999999"
                    )

                    db.add(cliente)
                    print("✅ Cliente criado")

                    # MOTORISTA
                    if db.query(Motorista).count() == 0:
                        motorista = Motorista(
                            nome="Motorista Teste",
                            telefone="5554999999998",
                            carro="Toyota Corolla",
                            placa="ABC1D23",
                            modelo="Corolla XEI",
                            ano=2022,
                            categoria="STANDARD",
                            status="ATIVO",
                            data_inicio_trial=datetime.utcnow(),
                            ativo=True,
                            plano="MASTER",
                            comissao_master=10.0
                        )

                        db.add(motorista)
                        print("✅ Motorista criado")

                        db.commit()

                        print("✅ Seed finalizado com sucesso")

    except Exception as e:
        db.rollback()
        print(f"❌ Erro no seed: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    seed()