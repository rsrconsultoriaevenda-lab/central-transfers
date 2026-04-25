from sqlalchemy.orm import Session
from backend.models import Servico


def criar_servico(db: Session, dados, usuario_id: int):
    # Ajustado para os campos reais do modelo Servico em models.py
    novo = Servico(
        nome=dados.nome if hasattr(dados, 'nome') else dados.tipo,
        tipo=dados.tipo,
        descricao=dados.descricao,
    )

    db.add(novo)
    db.commit()
    db.refresh(novo)

    return novo


def listar_servicos(db: Session):
    return db.query(Servico).filter(Servico.ativo == True).all()


def listar_servicos_por_usuario(db: Session, usuario_id: int):
    # Servico (categoria) não tem usuario_id no modelo atual.
    # Se precisar filtrar por usuário, a lógica deve ser nos Pedidos.
    return db.query(Servico).all()


def atualizar_status(db: Session, servico_id: int, status: str):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()

    if not servico:
        return None

    # O modelo Servico usa 'ativo' (bool). Mapeamos 'ativo'/'inativo' para booleano.
    servico.ativo = True if status.lower() == "ativo" else False

    db.commit()
    db.refresh(servico)

    return servico
