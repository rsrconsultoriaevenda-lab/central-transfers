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


def atribuir_motorista(db: Session, servico_id: int, motorista_id: int):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()
    if not servico:
        return None

    # Nota: O modelo Servico em models.py não possui motorista_id.
    # Essa lógica provavelmente deveria estar em Pedido.
    # servico.motorista_id = motorista_id 
    # servico.status = "atribuido"

    db.commit()
    db.refresh(servico)

    return servico


def atualizar_status(db: Session, servico_id: int, status: str):
    servico = db.query(Servico).filter(Servico.id == servico_id).first()

    if not servico:
        return None

    servico.status = status

    db.commit()
    db.refresh(servico)

    return servico
