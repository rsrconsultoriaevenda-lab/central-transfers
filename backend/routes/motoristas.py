from fastapi import APIRouter, HTTPException, Depends, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from backend.database import get_db, tenant_id
from backend import models, schemas
from backend.auth import get_usuario_atual, hash_senha
from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.services.email_templates import enviar_email_boas_vindas
import secrets

router = APIRouter(prefix="/motoristas", tags=["Motoristas"])


@router.get("/", response_model=List[schemas.Motorista])  # type: ignore
def listar(db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    # O Hook de multitenancy no database.py já filtra as queries automaticamente.
    # Apenas verificamos se o usuário logado tem permissão administrativa.
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Acesso negado. Apenas administradores podem ver a lista de motoristas.")

    # Reforço explícito de segurança para garantir isolamento por empresa_id
    current_tenant = tenant_id.get()
    return db.query(models.Motorista).filter(
        models.Motorista.empresa_id == current_tenant
    ).all()


@router.post("/localizacao")
async def atualizar_localizacao(request: Request, db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    """Recebe latitude e longitude do DriverApp e atualiza no banco."""
    data = await request.json()

    # No modo 'Acesso Livre', o user['email'] é fixo.
    # Em produção, usaríamos o ID do usuário vinculado ao motorista.
    email = user.get("email")

    # Busca o motorista (Lógica temporária para o admin simulado ou motorista real)
    if email == "admin@centraltransfers.com":
        motorista = db.query(models.Motorista).first()
    else:
        telefone = email.split("@")[0]
        motorista = db.query(models.Motorista).filter(
            models.Motorista.telefone == telefone).first()

    if not motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    motorista.latitude = data.get("latitude")
    motorista.longitude = data.get("longitude")
    motorista.ultima_atualizacao = datetime.now()

    db.commit()
    return {"status": "ok"}


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.MotoristaCreateResponse)
def register_motorista(motorista_data: schemas.MotoristaRegister, db: Session = Depends(get_db)):
    """
    Permite que um motorista se registre no sistema.
    O status inicial do motorista será 'PENDENTE_APROVACAO'.
    """
    # 1. Verificar se o telefone já está cadastrado como motorista
    if db.query(models.Motorista).filter(models.Motorista.telefone == motorista_data.telefone).first():
        raise HTTPException(
            status_code=400, detail="Telefone já cadastrado como motorista.")

    # 2. Verificar se o usuário de login já existe para este telefone
    email_login = f"{motorista_data.telefone}@motorista.com"
    if db.query(models.Usuario).filter(models.Usuario.email == email_login).first():
        raise HTTPException(
            status_code=400, detail="Usuário de login já existe para este telefone.")

    # 3. Criar a entrada de Usuário para o motorista
    novo_usuario = models.Usuario(
        email=email_login,
        senha=hash_senha(motorista_data.senha),
        role="motorista",
        # Para auto-registro, empresa_id pode ser None inicialmente ou vir do formulário
        empresa_id=motorista_data.empresa_id
    )
    db.add(novo_usuario)
    db.flush()  # Garante que o ID do usuário seja gerado antes de criar o motorista

    # 4. Criar a entrada de Motorista
    novo_motorista = models.Motorista(
        nome=motorista_data.nome,
        telefone=motorista_data.telefone,
        carro=motorista_data.carro,
        placa=motorista_data.placa,
        modelo=motorista_data.modelo,
        ano=motorista_data.ano,
        categoria=motorista_data.categoria,
        status="PENDENTE_APROVACAO",  # Status inicial para auto-registro
        plano="MENSAL",  # Plano padrão para novos registros
        empresa_id=motorista_data.empresa_id
    )
    db.add(novo_motorista)
    db.commit()
    db.refresh(novo_motorista)

    return {
        "motorista": novo_motorista,
        "acesso": {
            "login": email_login,
            "senha": "SENHA_OCULTA"  # Não retornar a senha em texto claro
        }
    }


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.MotoristaCreateResponse)
def criar(motorista: schemas.MotoristaBase, db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    senha_gerada = None
    try:
        # 1. Criar o registro do Motorista
        novo = models.Motorista(**motorista.model_dump())
        db.add(novo)

        # Flush garante que o objeto seja processado pelos hooks (como o de empresa_id)
        # antes de prosseguirmos para a criação do usuário.
        db.flush()

        # 2. Automação: Criar um Usuário de acesso para este motorista
        # Usamos o telefone como base para o login (ex: 54999999999@motorista.com)
        email_login = f"{motorista.telefone}@motorista.com"

        usuario_existente = db.query(models.Usuario).filter(
            models.Usuario.email == email_login).first()

        if not usuario_existente:
            # Gerar uma senha temporária aleatória
            senha_gerada = secrets.token_urlsafe(8)
            novo_usuario = models.Usuario(
                email=email_login,
                senha=hash_senha(senha_gerada),
                role="motorista",
                empresa_id=tenant_id.get()  # Vincula o motorista ao mesmo ID da empresa do Admin
            )
            db.add(novo_usuario)
            # Em produção, aqui você dispararia um SMS ou E-mail com a senha temporária.
            print(f"ACESSO GERADO: Login {email_login} | Senha {senha_gerada}")

        db.commit()
        db.refresh(novo)
        return {
            "motorista": novo,
            "acesso": {
                "login": email_login,
                "senha": senha_gerada
            }
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{motorista_id}/status", response_model=schemas.Motorista)
def update_motorista_status(
    motorista_id: int,
    status_update: schemas.MotoristaStatusUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    """Atualiza o status de um motorista (ex: ATIVO, PENDENTE_APROVACAO, REJEITADO)."""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Acesso negado. Apenas administradores podem alterar o status de motoristas.")

    motorista = db.query(models.Motorista).filter(
        models.Motorista.id == motorista_id).first()
    if not motorista:
        raise HTTPException(
            status_code=404, detail="Motorista não encontrado.")

    motorista.status = status_update.status
    db.commit()
    db.refresh(motorista)

    # Notificações Automáticas
    # Se o motorista for aprovado, inicia o período de trial
    if motorista.status == "ATIVO":
        mensagem = (
            f"🎉 Olá {motorista.nome}! Seu cadastro na Central Transfers foi APROVADO.\n\n"
            f"Você já pode acessar o aplicativo com seu telefone e a senha cadastrada para começar a receber viagens. Bem-vindo a bordo!"
        )
        background_tasks.add_task(
            enviar_whatsapp_meta, motorista.telefone, mensagem)
        motorista.data_inicio_trial = datetime.now()  # Define a data de início do trial
        background_tasks.add_task(enviar_email_boas_vindas, motorista)

    elif motorista.status == "REJEITADO":
        mensagem = (
            f"Olá {motorista.nome}. Informamos que sua solicitação de cadastro não foi aprovada neste momento.\n\n"
            f"Para mais informações ou dúvidas sobre os requisitos, entre em contato com o nosso suporte."
        )
        background_tasks.add_task(
            enviar_whatsapp_meta, motorista.telefone, mensagem)

    return motorista


@router.post("/verificar-expiracao-trials")
def verificar_expiracao_trials(
    background_tasks: BackgroundTasks, 
    db: Session = Depends(get_db), 
    user: dict = Depends(get_usuario_atual)
):
    """Varre motoristas cujo período de 14 dias expirou e atualiza status."""
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado.")

    agora = datetime.now()
    limite = agora - timedelta(days=14)

    expirados = db.query(models.Motorista).filter(
        models.Motorista.status == "ATIVO",
        models.Motorista.data_inicio_trial <= limite
    ).all()

    for m in expirados:
        m.status = "TRIAL_EXPIRADO"
        msg = f"Olá {m.nome}, seu período de teste de 14 dias terminou. Escolha um plano para continuar operando!"
        background_tasks.add_task(enviar_whatsapp_meta, m.telefone, msg)

    db.commit()
    return {"processados": len(expirados)}


@router.patch("/{motorista_id}")
def atualizar_plano_motorista(
    motorista_id: int,
    update_data: schemas.MotoristaBase,
    db: Session = Depends(get_db),
    email: str = Depends(get_usuario_atual)
):
    """Atualiza o modelo de cobrança (MENSAL ou MASTER) de um motorista."""
    db_motorista = db.query(models.Motorista).filter(
        models.Motorista.id == motorista_id).first()
    if not db_motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    db_motorista.plano = update_data.plano
    db.commit()
    db.refresh(db_motorista)
    return db_motorista


@router.get("/{motorista_id}/mensalidades", response_model=List[schemas.MensalidadeOut])
def listar_mensalidades(motorista_id: int, db: Session = Depends(get_db)):
    """Lista o histórico de mensalidades de um motorista específico."""
    return db.query(models.Mensalidade).filter(models.Mensalidade.motorista_id == motorista_id).all()


@router.post("/{motorista_id}/mensalidades/gerar")
def gerar_mensalidade(motorista_id: int, valor: float, mes: str, db: Session = Depends(get_db)):
    """Gera manualmente uma cobrança de mensalidade."""
    nova = models.Mensalidade(
        motorista_id=motorista_id,
        mes_referencia=mes,
        valor=valor,
        status="PENDENTE"
    )
    db.add(nova)
    db.commit()
    return {"status": "Mensalidade gerada"}


@router.post("/mensalidades/{mensalidade_id}/pagar")
def registrar_pagamento_mensalidade(mensalidade_id: int, db: Session = Depends(get_db)):
    """Registra que o motorista pagou a mensalidade."""
    mensalidade = db.query(models.Mensalidade).filter(
        models.Mensalidade.id == mensalidade_id).first()
    if not mensalidade:
        raise HTTPException(
            status_code=404, detail="Mensalidade não encontrada")
    mensalidade.status = "PAGO"
    mensalidade.data_pagamento = datetime.now()
    db.commit()
    return {"status": "Pagamento registrado"}
