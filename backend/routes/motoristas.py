import logging
from fastapi import APIRouter, HTTPException, Depends, status, Request, BackgroundTasks, logger
from sqlalchemy import func
from sqlalchemy.orm import Session
from typing import List
# Importe as configurações, se estiver usando
from datetime import datetime, timedelta
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_usuario_atual, hash_senha
from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.services.email_templates import enviar_email_boas_vindas
from backend.services.pagamento_service import criar_checkout_pro
from backend.utils.phone import formatar_telefone_e164
from decimal import Decimal
import secrets

router = APIRouter(prefix="/motoristas", tags=["Motoristas"])


@router.get("/", response_model=List[schemas.Motorista])  # type: ignore
def listar(db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    return db.query(models.Motorista).all()


@router.post("/localizacao")
async def atualizar_localizacao(request: Request, db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    """Recebe latitude e longitude do DriverApp e atualiza no banco."""
    data = await request.json()

    motorista = None
    # No modo 'Acesso Livre', o user['email'] é fixo.
    # Em produção, usaríamos o ID do usuário vinculado ao motorista.
    email = user.get("email")
    role = user.get("role")

    # Se não for admin, busca pelo telefone atrelado ao e-mail de login
    if role != "admin":
        telefone = email.split("@")[0]
        motorista = db.query(models.Motorista).filter(
            models.Motorista.telefone == telefone).first()

    if not motorista:
        # Caso seja admin testando, pegamos o primeiro motorista para não travar o fluxo
        if role == "admin":
            motorista = db.query(models.Motorista).first()

        if not motorista:
            raise HTTPException(
                status_code=404, detail="Motorista não encontrado")

    motorista.latitude = data.get("latitude")
    motorista.longitude = data.get("longitude")
    motorista.ultima_atualizacao = datetime.now()

    db.commit()
    return {"status": "ok"}


@router.get("/me/saldo", response_model=schemas.MotoristaSaldo)
def consultar_saldo_proprio(db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    """Permite que o motorista logado consulte seu saldo de corridas concluídas."""
    email = user.get("email")
    # Tenta encontrar o motorista pelo telefone (extraído do e-mail de login)
    telefone = email.split("@")[0]
    motorista = db.query(models.Motorista).filter(
        models.Motorista.telefone == telefone).first()

    if not motorista:
        raise HTTPException(
            status_code=404, detail="Perfil de motorista não encontrado.")

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


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=schemas.MotoristaCreateResponse)
def register_motorista(motorista_data: schemas.MotoristaRegister, db: Session = Depends(get_db)):
    """
    Permite que um motorista se registre no sistema.
    O status inicial do motorista será 'PENDENTE_APROVACAO'.
    """
    # Padroniza o telefone antes de checar/salvar
    try:
        telefone_limpo = formatar_telefone_e164(motorista_data.telefone)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 1. Verificar se o telefone já está cadastrado como motorista
    if db.query(models.Motorista).filter(models.Motorista.telefone == telefone_limpo).first():
        raise HTTPException(
            status_code=400, detail="Telefone já cadastrado como motorista.")

    email_login = f"{telefone_limpo}@motorista.com"
    if db.query(models.Usuario).filter(models.Usuario.email == email_login).first():
        raise HTTPException(
            status_code=400, detail="Usuário de login já existe para este telefone.")

    # 3. Criar a entrada de Usuário para o motorista
    novo_usuario = models.Usuario(
        email=email_login,
        senha=hash_senha(motorista_data.senha),
        role="motorista"
    )
    db.add(novo_usuario)
    db.flush()  # Garante que o ID do usuário seja gerado antes de criar o motorista

    # 4. Criar a entrada de Motorista
    novo_motorista = models.Motorista(
        nome=motorista_data.nome,
        telefone=telefone_limpo,
        carro=motorista_data.carro,
        placa=motorista_data.placa,
        modelo=motorista_data.modelo,
        ano=motorista_data.ano,
        categoria=motorista_data.categoria,
        status="PENDENTE_APROVACAO",  # Status inicial para auto-registro
        plano="MENSAL"  # Plano padrão para novos registros
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
def criar(motorista_data: schemas.MotoristaCreateAdmin, db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    """Criação de motorista via Painel Administrativo."""
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Acesso negado. Apenas administradores podem cadastrar motoristas.")

    try:
        # Cria a instância de Motorista, excluindo 'senha' do dump, pois models.Motorista não possui esse campo
        novo = models.Motorista(**motorista_data.model_dump(exclude={"senha"}))
        db.add(novo)
        db.flush()

        email_login = f"{motorista_data.telefone}@motorista.com"
        # Usa a senha fornecida pelo admin, se houver
        senha_para_usuario = motorista_data.senha

        usuario_existente = db.query(models.Usuario).filter(
            models.Usuario.email == email_login).first()

        # Valor padrão para usuário existente ou senha não gerada
        senha_retornada = "JA_CADASTRADA"

        if usuario_existente:
            # Se o usuário já existe e uma nova senha foi fornecida pelo admin, atualiza.
            if senha_para_usuario:
                usuario_existente.senha = hash_senha(senha_para_usuario)
                db.add(usuario_existente)  # Marca para atualização
                senha_retornada = senha_para_usuario
            # Caso contrário, se o usuário existe e nenhuma senha nova foi fornecida, mantém a existente.
        else:
            # Se o usuário não existe, cria um novo
            if not senha_para_usuario:  # Se nenhuma senha foi fornecida pelo admin, gera uma
                senha_para_usuario = secrets.token_urlsafe(8)

            novo_usuario = models.Usuario(
                email=email_login,
                senha=hash_senha(senha_para_usuario),
                role="motorista"
            )
            db.add(novo_usuario)
            senha_retornada = senha_para_usuario  # Armazena a senha que foi usada/gerada

        db.commit()
        db.refresh(novo)
        return {
            "motorista": novo,
            "acesso": {
                "login": email_login,
                "senha": senha_retornada
            }
        }
    except Exception as e:
        db.rollback()
        error_msg = str(e).lower()
        if "duplicate" in error_msg or "already exists" in error_msg:
            raise HTTPException(
                status_code=400, detail="Este telefone ou e-mail já está em uso por outro motorista.")
        # Log no terminal para investigação
        print(f"ERRO CRÍTICO NO CADASTRO: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Erro no banco de dados: {str(e)}")


@router.patch("/{motorista_id}")
def atualizar_plano_motorista(
    motorista_id: int,
    update_data: schemas.MotoristaBase,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_usuario_atual)
):
    """Atualiza o modelo de cobrança (MENSAL ou MASTER) de um motorista."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=403, detail="Acesso negado. Apenas administradores podem alterar planos.")

    db_motorista = db.query(models.Motorista).filter(
        models.Motorista.id == motorista_id).first()
    if not db_motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    # Apenas atualiza o plano se ele for diferente do atual
    if db_motorista.plano != update_data.plano:
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


@router.post("/mensalidades/processar-automatico")
def processar_mensalidades_automaticas(db: Session = Depends(get_db), user: dict = Depends(get_usuario_atual)):
    """
    Gera mensalidades automaticamente para motoristas no plano MENSAL.
    Verifica se o trial acabou e se a mensalidade do mês atual já existe.
    """
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    agora = datetime.now()
    mes_atual = agora.strftime("%Y-%m")

    # Buscamos motoristas no plano MENSAL que estão ativos ou com trial expirado
    motoristas = db.query(models.Motorista).filter(
        models.Motorista.plano == "MENSAL",
        models.Motorista.status.in_(["ATIVO", "TRIAL_EXPIRADO"])
    ).all()

    geradas = 0
    for m in motoristas:
        # Se tiver data de início de trial, verifica se o período de 14 dias já passou
        if m.data_inicio_trial:
            fim_trial = m.data_inicio_trial + timedelta(days=14)
            if agora < fim_trial:
                continue

        # Verifica se já existe mensalidade gerada para este motorista neste mês específico
        existe = db.query(models.Mensalidade).filter(
            models.Mensalidade.motorista_id == m.id,
            models.Mensalidade.mes_referencia == mes_atual
        ).first()

        if not existe:
            valor_mensalidade = Decimal("150.00")
            nova = models.Mensalidade(
                motorista_id=m.id,
                mes_referencia=mes_atual,
                valor=valor_mensalidade,
                # Vencimento sugerido para 5 dias após a geração
                data_vencimento=agora + timedelta(days=5),
                status="PENDENTE"
            )
            db.add(nova)
            db.flush() # Para obter o ID antes de gerar o link
            
            # Gerar link do Mercado Pago
            try:
                link = criar_checkout_pro(nova.id, float(valor_mensalidade), f"Mensalidade {mes_atual} - Central Transfers", item_type="MENSAL")
                nova.checkout_url = link
            except Exception as e:
                logger.error(f"Erro ao gerar link Mercado Pago para motorista {m.id}: {str(e)}")

            db.add(nova)
            geradas += 1

    db.commit()
    return {"status": "sucesso", "mensalidades_geradas": geradas}


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
