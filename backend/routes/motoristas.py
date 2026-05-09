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

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.database import get_db
from backend import models, schemas, config
from backend.auth import get_usuario_atual, hash_senha, get_usuario_opcional
from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.services.email_templates import enviar_email_boas_vindas
from backend.services.pagamento_service import criar_checkout_pro
from backend.utils.phone import formatar_telefone_e164

router = APIRouter(
    prefix="/motoristas",
    tags=["Motoristas"]
)

logger = logging.getLogger(__name__)


# ---------------------------
# LISTAR MOTORISTAS
# ---------------------------
@router.get("/", response_model=List[schemas.Motorista])
def listar(db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    return db.query(models.Motorista).all()


# ---------------------------
# ATUALIZAR LOCALIZAÇÃO
# ---------------------------
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

    # ---------------------------
    # SALDO MOTORISTA
    # ---------------------------


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


# ---------------------------
# REGISTRO MOTORISTA (AUTO)
# ---------------------------
@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MotoristaCreateResponse
)
def register_motorista(motorista_data: schemas.MotoristaRegister, db: Session = Depends(get_db)):

    try:
        telefone_limpo = formatar_telefone_e164(motorista_data.telefone)
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
        senha=hash_senha(motorista_data.senha),
        role="motorista"
    )

    db.add(novo_usuario)
    db.flush()

    novo_motorista = models.Motorista(
        nome=motorista_data.nome,
        telefone=telefone_limpo,
        carro=motorista_data.carro,
        placa=motorista_data.placa,
        modelo=motorista_data.modelo,
        ano=motorista_data.ano,
        categoria=motorista_data.categoria,
        status="PENDENTE_APROVACAO",
        plano="MENSAL"
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


# ---------------------------
# CRIAÇÃO ADMIN
# ---------------------------
@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.MotoristaCreateResponse
)
def criar(
    motorista_data: schemas.MotoristaCreateAdmin,
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):

    if user.get("role") != "admin":
        raise HTTPException(403, "Acesso negado")

    try:
        novo = models.Motorista(
            **motorista_data.model_dump(exclude={"senha", "comissao_master"}),
            comissao_master=getattr(motorista_data, 'comissao_master', 10.0)
        )

        db.add(novo)
        db.flush()

        email_login = f"{motorista_data.telefone}@motorista.com"
        senha_plana = motorista_data.senha or secrets.token_urlsafe(8)

        usuario_existente = db.query(models.Usuario).filter(
            models.Usuario.email == email_login
        ).first()

        if not usuario_existente:
            novo_usuario = models.Usuario(
                email=email_login,
                senha=hash_senha(senha_plana),
                role="motorista"
            )
            db.add(novo_usuario)
        elif motorista_data.senha:
            usuario_existente.senha = hash_senha(motorista_data.senha)

        db.commit()
        db.refresh(novo)
        return {
            "motorista": novo,
            "acesso": {"login": email_login, "senha": senha_plana if not usuario_existente else "ALTERADA_OU_EXISTENTE"}
        }

    except Exception as e:
        db.rollback()
        logger.error(f"ERRO: {str(e)}", exc_info=True)
        raise HTTPException(500, str(e))

    # ---------------------------
    # MENSALIDADES AUTOMÁTICAS
    # ---------------------------


@router.post("/mensalidades/processar-automatico")
def processar_mensalidades_automaticas(
    db: Session = Depends(get_db),
    user: Optional[dict] = Depends(get_usuario_opcional),
    x_cron_key: str = Header(None)
):
    is_cron = (
        x_cron_key == config.settings.MERCADO_PAGO_WEBHOOK_SECRET
    )

    # Verifica se é um admin logado ou se a chave de cron está correta
    is_admin = user and user.get("role") == "admin"

    agora = datetime.now()
    mes_atual = agora.strftime("%Y-%m")

    motoristas = db.query(models.Motorista).filter(
        models.Motorista.plano == "MENSAL",
        models.Motorista.status.in_(["ATIVO", "TRIAL_EXPIRADO"])
    ).all()

    geradas = 0

    for m in motoristas:

        if m.data_inicio_trial:
            if agora < m.data_inicio_trial + timedelta(days=14):
                continue

            existe = db.query(models.Mensalidade).filter(
                models.Mensalidade.motorista_id == m.id,
                models.Mensalidade.mes_referencia == mes_atual
            ).first()

            if existe:
                continue

            # Sugestão de valor mais condizente com o mercado de transfers
            valor = Decimal(str(getattr(
                config.settings,
                "VALOR_MENSALIDADE",
                "299.00"
            )))

            nova = models.Mensalidade(
                motorista_id=m.id,
                mes_referencia=mes_atual,
                valor=valor,
                data_vencimento=agora + timedelta(days=5),
                status="PENDENTE"
            )

            db.add(nova)
            db.flush()

            try:
                nova.checkout_url = criar_checkout_pro(
                    nova.id,
                    float(valor),
                    f"Mensalidade {mes_atual}",
                    item_type="MENSAL"
                )
            except Exception as e:
                logger.error(f"Erro checkout {m.id}: {str(e)}")

            geradas += 1

    db.commit()

    return {
        "status": "sucesso",
        "mensalidades_geradas": geradas
    }

    # ---------------------------
    # TRIAL EXPIRADO
    # ---------------------------


@router.post("/verificar-expiracao-trials")
def verificar_expiracao_trials(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):

    if user.get("role") != "admin":
        raise HTTPException(403, "Acesso negado")

    agora = datetime.now()
    limite = agora - timedelta(days=14)

    expirados = db.query(models.Motorista).filter(
        models.Motorista.status == "ATIVO",
        models.Motorista.data_inicio_trial <= limite
    ).all()

    for m in expirados:
        m.status = "TRIAL_EXPIRADO"

        background_tasks.add_task(
            enviar_whatsapp_meta,
            m.telefone,
            f"Olá {m.nome}, seu trial terminou."
        )

    db.commit()

    return {"processados": len(expirados)}
