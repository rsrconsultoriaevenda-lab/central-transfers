import logging
import secrets

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Request,
    BackgroundTasks,
    Header
)

from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.database import get_db
from backend import models, schemas, config
from backend.auth import (
    get_usuario_atual,
    get_usuario_opcional,
    hash_senha
)

from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.services.pagamento_service import criar_checkout_pro
from backend.utils.phone import formatar_telefone_e164

router = APIRouter(
    prefix="/motoristas",
    tags=["Motoristas"]
)

logger = logging.getLogger(__name__)


# =====================================================
# LISTAR MOTORISTAS
# =====================================================

@router.get("/", response_model=List[schemas.Motorista])
def listar(
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    return db.query(models.Motorista).all()


# =====================================================
# ATUALIZAR LOCALIZAÇÃO
# =====================================================

@router.post("/localizacao")
async def atualizar_localizacao(
    request: Request,
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):

    data = await request.json()

    email = user.get("email")
    role = user.get("role")

    motorista = None

    if role != "admin":

        telefone = email.split("@")[0]

        motorista = db.query(models.Motorista).filter(
            models.Motorista.telefone == telefone
        ).first()
    else:
        motorista = db.query(models.Motorista).first()

    if not motorista:
        raise HTTPException(404, "Motorista não encontrado")

    motorista.latitude = data.get("latitude")
    motorista.longitude = data.get("longitude")
    motorista.ultima_atualizacao = datetime.now()
    db.commit()
    return {"status": "ok"}


# =====================================================
# CONSULTAR SALDO
# =====================================================

@router.get("/me/saldo", response_model=schemas.MotoristaSaldo)
def consultar_saldo_proprio(
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):

    email = user.get("email")
    telefone = email.split("@")[0]

    motorista = db.query(models.Motorista).filter(
        models.Motorista.telefone == telefone
    ).first()

    if not motorista:
        raise HTTPException(404, "Perfil de motorista não encontrado")

    stats = db.query(
        func.sum(models.Pedido.valor_liquido_motorista).label("saldo"),
        func.count(models.Pedido.id).label("total")
    ).filter(
        models.Pedido.motorista_id == motorista.id,
        models.Pedido.status == "CONCLUIDO"
    ).first()

    return {
        "saldo_total": stats.saldo or Decimal("0.00"),
        "total_pedidos": stats.total or 0
    }


# =====================================================
# REGISTRO AUTOMÁTICO MOTORISTA
# =====================================================

@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MotoristaCreateResponse
)
def register_motorista(
    motorista_data: schemas.MotoristaRegister,
    db: Session = Depends(get_db)
):

    try:

        telefone_limpo = formatar_telefone_e164(
            motorista_data.telefone
        )

    except ValueError as e:

        raise HTTPException(400, str(e))

    motorista_existente = db.query(models.Motorista).filter(
        models.Motorista.telefone == telefone_limpo
    ).first()

    if motorista_existente:
        raise HTTPException(400, "Telefone já cadastrado")

    email_login = f"{telefone_limpo}@motorista.com"

    usuario_existente = db.query(models.Usuario).filter(
        models.Usuario.email == email_login
    ).first()

    if usuario_existente:
        raise HTTPException(400, "Usuário já existe")

    novo_usuario = models.Usuario(
        email=email_login,
        senha_hash=hash_senha(motorista_data.senha),
        role="motorista"
    )

    db.add(novo_usuario)
    db.flush()

    novo_motorista = models.Motorista(
        nome=motorista_data.nome,
        email=email_login,
        senha_hash=hash_senha(motorista_data.senha),
        telefone=telefone_limpo,
        carro=motorista_data.carro,
        placa=motorista_data.placa,
        modelo=motorista_data.modelo,
        ano=motorista_data.ano,
        categoria=motorista_data.categoria,
        status="PENDENTE_APROVACAO",
        plano="MENSAL",
        data_inicio_trial=datetime.now()
    )

    db.add(novo_motorista)

    db.commit()
    db.refresh(novo_motorista)

    return {
        "motorista": novo_motorista,
        "acesso": {
            "login": email_login,
            "senha": "SENHA_OCULTA"
        }
    }
