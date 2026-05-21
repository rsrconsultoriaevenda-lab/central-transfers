import logging
import secrets
from datetime import datetime
from decimal import Decimal
from typing import List

from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    status,
    Request
)
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func

from backend.database import get_db
from backend import models, schemas
from backend.auth import (
    get_usuario_atual,
    hash_senha
)
from backend.utils.phone import formatar_telefone_e164

# Criamos o roteador sem travar caminhos rígidos
router = APIRouter()

logger = logging.getLogger(__name__)

# =====================================================
# LISTAR MOTORISTAS (ACEITA / OU STRING VAZIA)
# =====================================================


@router.get("/", response_model=List[schemas.Motorista])
@router.get("", response_model=List[schemas.Motorista])
def listar_motoristas(
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")
    return db.query(models.Motorista).options(joinedload(models.Motorista.mensalidades)).all()


# =====================================================
# CRIAR MOTORISTA (ADMIN) - ENTRADA DINÂMICA
# =====================================================
@router.post("/", response_model=schemas.MotoristaCreateResponse)
@router.post("", response_model=schemas.MotoristaCreateResponse)
async def criar_motorista_admin(
    motorista_in: schemas.MotoristaCreateAdmin,
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    # SEGURANÇA: Apenas administradores podem criar motoristas por esta rota
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        telefone_limpo = formatar_telefone_e164(motorista_in.telefone)
    except ValueError as e:
        raise HTTPException(400, str(e))

    # Verifica se já existe perfil cadastrado com esse telefone
    if db.query(models.Motorista).filter(models.Motorista.telefone == telefone_limpo).first():
        raise HTTPException(
            400, "Este telefone já está cadastrado para um motorista.")

    # Gera credenciais padrão baseadas no formato telefônico
    email_login = f"{telefone_limpo}@motorista.com"
    senha_plana = motorista_in.senha or secrets.token_urlsafe(8)

    try:
        # 1. Cria o Usuário de Sistema (Autenticação)
        novo_usuario = models.Usuario(
            email=email_login,
            senha_hash=hash_senha(senha_plana),
            role="motorista"
        )
        db.add(novo_usuario)
        db.flush()  # Popula o ID na sessão do SQLAlchemy

        # Mapeia o plano recebido do front de forma limpa
        plano_formatado = "MASTER" if "20%" in str(
            motorista_in.plano) else str(motorista_in.plano)

        # 2. Cria o Perfil do Motorista (Logística)
        novo_motorista = models.Motorista(
            nome=motorista_in.nome,
            email=email_login,
            telefone=telefone_limpo,
            senha_hash=novo_usuario.senha_hash,  # Sincroniza hash
            carro=motorista_in.carro,
            placa=motorista_in.placa,
            modelo=motorista_in.modelo or motorista_in.carro,
            ano=motorista_in.ano or 2024,
            categoria=motorista_in.categoria or "STANDARD",
            plano=plano_formatado,
            status="ATIVO",
            data_inicio_trial=datetime.now()
        )
        db.add(novo_motorista)

        db.commit()
        return {
            "motorista": novo_motorista,
            "acesso": {
                "login": email_login,
                "senha": senha_plana,
                "status": "success"
            }
        }

    except Exception as e:
        db.rollback()
        logger.error(f"Erro ao salvar motorista no banco: {str(e)}")
        raise HTTPException(500, f"Erro interno ao salvar os dados: {str(e)}")

# =====================================================
# ATUALIZAR LOCALIZAÇÃO GEOFENCING
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

    if role != "admin":
        motorista = db.query(models.Motorista).filter(
            models.Motorista.email == email
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
# CONSULTAR SALDO FINANCEIRO (CORRIDAS)
# =====================================================
@router.get("/me/saldo")
def consultar_saldo_proprio(
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    email = user.get("email")
    motorista = db.query(models.Motorista).filter(
        models.Motorista.email == email
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
# REGISTRO AUTOMÁTICO MOTORISTA (AUTO-CADASTRO)
# =====================================================
@router.post("/register")
async def register_motorista(
    motorista_in: schemas.MotoristaRegister,
    db: Session = Depends(get_db)
):

    try:
        telefone_limpo = formatar_telefone_e164(motorista_in.telefone)
    except ValueError as e:
        raise HTTPException(400, str(e))

    if db.query(models.Motorista).filter(models.Motorista.telefone == telefone_limpo).first():
        raise HTTPException(400, "Telefone já cadastrado")

    email_login = f"{telefone_limpo}@motorista.com"

    if db.query(models.Usuario).filter(models.Usuario.email == email_login).first():
        raise HTTPException(400, "Usuário já existe")

    try:
        novo_usuario = models.Usuario(
            email=email_login,
            senha_hash=hash_senha(motorista_in.senha),
            role="motorista"
        )
        db.add(novo_usuario)
        db.flush()

        novo_motorista = models.Motorista(
            nome=motorista_in.nome,
            email=email_login,
            telefone=telefone_limpo,
            carro=motorista_in.carro,
            placa=motorista_in.placa,
            modelo=motorista_in.modelo or motorista_in.carro,
            ano=motorista_in.ano or 2024,
            categoria=motorista_in.categoria or "STANDARD",
            status="PENDENTE_APROVACAO",
            plano="MENSAL",
            data_inicio_trial=datetime.now()
        )
        db.add(novo_motorista)
        db.commit()

        return {
            "status": "success",
            "mensagem": "Cadastro realizado! Aguardando aprovação administrativa."
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(500, f"Erro interno no auto-registro: {str(e)}")
