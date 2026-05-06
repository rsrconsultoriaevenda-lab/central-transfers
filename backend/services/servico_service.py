from sqlalchemy.orm import Session
from backend.models import Servico
from backend.database import tenant_id


def criar_servico(db: Session, dados, usuario_id: int = None):
    # Ajustado para os campos reais do modelo Servico em models.py
    current_tenant = tenant_id.get()
    novo = Servico(
        nome=dados.nome if hasattr(dados, 'nome') else dados.tipo,
        tipo=dados.tipo if hasattr(dados, 'tipo') else "Geral",
        categoria=dados.categoria if hasattr(
            dados, 'categoria') else "TRANSFERS",
        valor=dados.valor if hasattr(dados, 'valor') else 0.0,
        descricao=dados.descricao,
        imagem_url=dados.imagem_url if hasattr(dados, 'imagem_url') else None,
        empresa_id=dados.empresa_id if (
            hasattr(dados, 'empresa_id') and dados.empresa_id) else current_tenant
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
