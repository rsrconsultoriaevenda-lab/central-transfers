from backend.database import SessionLocal
from backend.models import Servico
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))


def seed():
    print("=== Populando Banco de Dados com Serviços Iniciais ===")
    db = SessionLocal()

    servicos_iniciais = [
        {"nome": "Tour Gramado", "tipo": "Tour",
            "descricao": "Passeio pelos principais pontos turísticos de Gramado e Canela."},
        {"nome": "Tour Uva e Vinho", "tipo": "Tour",
            "descricao": "Visita a vinícolas na região de Bento Gonçalves com almoço típico."},
        {"nome": "Transfer Aeroporto", "tipo": "Transfer",
            "descricao": "Transporte privativo do Aeroporto de POA para Gramado/Canela."},
        {"nome": "Carro a disposição", "tipo": "Carro à disposição",
            "descricao": "Motorista privativo por período de 8 horas."},
    ]

    try:
        for s in servicos_iniciais:
            existe = db.query(Servico).filter(
                Servico.nome == s["nome"]).first()
            if not existe:
                novo_servico = Servico(**s)
                db.add(novo_servico)
                print(f"Adicionando: {s['nome']}")

        db.commit()
        print("\nSincronização concluída com sucesso!")
    except Exception as e:
        db.rollback()
        print(f"Erro ao popular banco: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
