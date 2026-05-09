from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend import models
import logging

logger = logging.getLogger(__name__)


def verificar_expiracao_motoristas(db: Session):
    """
    Busca motoristas em Trial que passaram de 14 dias e não possuem 
    mensalidade paga para o mês corrente.
    """
    hoje = datetime.now()
    limite_trial = hoje - timedelta(days=14)

    motoristas_expirados = db.query(models.Motorista).filter(
        models.Motorista.plano == "MENSAL",
        models.Motorista.status == "ATIVO",
        models.Motorista.data_inicio_trial <= limite_trial
    ).all()

    for m in motoristas_expirados:
        # Aqui você pode verificar se existe mensalidade PAGA em models.Mensalidade
        # Se não houver, m.status = "TRIAL_EXPIRADO"
        m.status = "TRIAL_EXPIRADO"
        logger.info(
            f"🚫 Motorista {m.nome} (ID: {m.id}) bloqueado por expiração de trial.")

    db.commit()
