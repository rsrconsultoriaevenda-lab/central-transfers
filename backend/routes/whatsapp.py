from datetime import datetime
import re
import logging
from fastapi import APIRouter, HTTPException, Query, Depends, Response, Request
from sqlalchemy.orm import Session
from typing import Optional
from backend import models, schemas
from backend.config import settings
from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.database import get_db
router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

# Configuração de Log para monitorar automações
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_MAP = {
    "gramado": ("Tour Gramado", "Tour"),
    "uva": ("Tour Uva e Vinho", "Tour"),
    "vinho": ("Tour Uva e Vinho", "Tour"),
    "bento": ("Bento Gonçalves", "Tour"),
    "disposicao": ("Carro a disposição", "Carro à disposição"),
    "disponibilidade": ("Carro a disposição", "Carro à disposição"),
    "transfer": ("Transfer", "Transfer"),
}

PAYMENT_METHOD = "PIX ou transferência bancária"
CENTRAL_BANK_DETAILS = (
    "R.DE S.ROCHA LTDA / favorecido Renato de Souza Rocha\n"
    "Banco: 336 - C6 S.A.\n"
    "Agência: 0001\n"
    "Conta corrente: 35224666-9\n"
    "PIX: 58.011.293/0001-92\n"
)
COMMISSION_NOTE = "A central recebe o valor e repassa a comissão para o motorista após a viagem."


def _clean_text(value: str):
    if not value:
        return None
    return value.strip().strip(". ")


def _parse_field(text: str, label: str):
    lower = text.lower()
    idx = lower.find(label)
    if idx < 0:
        return None
    start = idx + len(label)
    remainder = text[start:]
    separators = ["\n", ";", ".", ","]
    end = len(remainder)
    for sep in separators:
        sep_idx = remainder.find(sep)
        if sep_idx != -1 and sep_idx < end:
            end = sep_idx
    return _clean_text(remainder[:end])


def _guess_service(message: str):
    lower = message.lower()
    for key, (name, tipo) in SERVICE_MAP.items():
        if key in lower:
            return name, tipo
    return None, None


def _parse_price(message: str):
    match = re.search(
        r"valor\s*[:\-]?\s*([0-9]+[\.,]?[0-9]*)", message.lower())
    if match:
        return float(match.group(1).replace(",", "."))
    return 0.0


def _parse_date(message: str):
    raw = _parse_field(message, "data:") or _parse_field(message, "em:")
    if not raw:
        return datetime.now()

    raw = raw.replace(" às ", " ").replace(" as ", " ").replace("h", ":")

    formatos = ["%Y-%m-%dT%H:%M", "%d/%m/%Y %H:%M",
                "%d/%m/%Y", "%Y-%m-%d %H:%M", "%d/%m/%y %H:%M",
                "%d-%m-%Y %H:%M", "%d/%m/%Y %H:%M:%S"]
    for fmt in formatos:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(raw.split(".")[0])
    except ValueError:
        return datetime.now()


def _parse_order_id(message: str):
    match = re.search(r"pedido\s*#?\s*(\d+)", message.lower())
    if match:
        return int(match.group(1))
    return None


def _find_or_create_user_by_phone(db: Session, phone: str):
    # Como o novo modelo Usuario usa email, vamos simular um email pelo telefone para integração via Zap
    email_simulado = f"{phone}@whatsapp.com"
    usuario = db.query(models.Usuario).filter(
        models.Usuario.email == email_simulado).first()
    if usuario:
        return usuario

    novo_usuario = models.Usuario(
        email=email_simulado, senha="login_via_whatsapp")
    db.add(novo_usuario)
    db.commit()
    db.refresh(novo_usuario)
    return novo_usuario


def _find_or_create_service(db: Session, nome: str, tipo: str):
    servico = db.query(models.Servico).filter(
        models.Servico.nome == nome).first()
    if servico:
        return servico

    novo_servico = models.Servico(
        nome=nome,
        tipo=tipo,
        descricao=f"Serviço gerado automaticamente para {nome}"
    )
    db.add(novo_servico)
    db.commit()
    db.refresh(novo_servico)
    return novo_servico


def _find_or_create_client(db: Session, phone: str):
    # Placeholder para _find_or_create_client
    # Em um cenário real, você buscaria por telefone e criaria se não encontrado.
    # Por enquanto, vamos criar um cliente dummy ou levantar um erro se não encontrado.
    cliente = db.query(models.Cliente).filter(
        models.Cliente.telefone == phone).first()
    if cliente:
        return cliente

    novo_cliente = models.Cliente(
        nome=f"Cliente WhatsApp {phone}", telefone=phone)
    db.add(novo_cliente)
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente


def _broadcast_to_drivers(db: Session, pedido: models.Pedido):
    motoristas = db.query(models.Motorista).filter(
        models.Motorista.telefone != None).all()
    mensagens = []
    for motorista in motoristas:
        try:
            status_code, response = enviar_whatsapp_meta(
                motorista.telefone,
                (  # Alterado de corrida para pedido
                    f"Novo Pedido {pedido.id} disponível: De {pedido.origem} para {pedido.destino} em {pedido.data_servico.strftime('%d/%m/%Y %H:%M')}."
                    f" Responda no painel para aceitar."
                ),
            )
            mensagens.append({"telefone": motorista.telefone,
                             "status": status_code, "response": response})
        except Exception as e:
            logger.error(f"Falha ao notificar motorista {motorista.id}: {e}")
            continue
    return mensagens


@router.get("/incoming")
def verify_whatsapp_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
    hub_verify_token: str = Query(None, alias="hub.verify_token")
):
    """Endpoint para verificação do Webhook da Meta API."""
    logger.info(
        f"Recebendo tentativa de verificação Meta: mode={hub_mode}, token={hub_verify_token}")
    verify_token = settings.WHATSAPP_VERIFY_TOKEN

    if not verify_token:
        logger.error(
            "WHATSAPP_VERIFY_TOKEN não configurado nas variáveis de ambiente.")
        raise HTTPException(
            status_code=500, detail="Configuração de servidor incompleta")

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        logger.info(
            f"✅ Webhook verificado com sucesso! Token: {hub_verify_token}")
        return Response(content=hub_challenge, media_type="text/plain")

    logger.warning(
        f"❌ Falha na verificação!\nEsperado: {verify_token}\nRecebido: {hub_verify_token}"
    )
    raise HTTPException(
        status_code=403, detail="Token de verificação inválido")


@router.post("/incoming")
async def whatsapp_incoming(request: Request, db: Session = Depends(get_db)):
    """
    Processa mensagens recebidas da Meta API ou de simuladores.
    """
    data = await request.json()
    logger.info(f"Payload bruto recebido do WhatsApp: {data}")

    # Tenta extrair dados no formato da Meta API
    sender = None
    message = None

    try:
        if "entry" in data:
            # Formato Real da Meta
            value = data["entry"][0]["changes"][0]["value"]
            if "messages" in value:
                msg_obj = value["messages"][0]
                sender = msg_obj.get("from")
                message = msg_obj.get("text", {}).get("body")
        else:
            # Formato Simplificado (para testes manuais via Postman)
            sender = data.get("sender")
            message = data.get("message")
    except (KeyError, IndexError):
        logger.warning(f"Payload recebido em formato desconhecido: {data}")
        return {"status": "ignored", "reason": "invalid_format"}

    if not sender or not message:
        return {"status": "ignored", "reason": "no_content"}

    logger.info(
        f"[WHATSAPP RECEBIDO] Remetente: {sender} | Conteúdo: {message}")

    message = message.strip()
    lower = message.lower()

    if "pago" in lower or "pagamento" in lower:
        cliente = _find_or_create_client(db, sender)
        order_id = _parse_order_id(lower)

        pedido = None
        if order_id:  # Agora usando models.Pedido
            pedido = db.query(models.Pedido).filter(
                models.Pedido.id == order_id).first()

        if not pedido:
            pedido = db.query(models.Pedido).filter(
                models.Pedido.cliente_id == cliente.id,
                models.Pedido.status == 'AGUARDANDO_PAGAMENTO'
            ).order_by(models.Pedido.id.desc()).first()

        if not pedido:
            text = (
                "Não encontrei um pedido pendente para pagamento. Envie 'pedido origem: ... destino: ... data: ... valor: ...' para criar um pedido ou 'pago pedido <id>' se você já tiver um pedido."
            )
            enviar_whatsapp_meta(sender, text)
            return {"status": "pedido_nao_encontrado", "mensagem": text}

        if pedido.status == "PAGO":
            text = f"O pedido {pedido.id} já está marcado como pago. Aguardando motorista aceitar."
            enviar_whatsapp_meta(sender, text)
            return {"status": "ja_pago", "pedido_id": pedido.id, "mensagem": text}

        pedido.status = 'PAGO'
        db.commit()
        db.refresh(pedido)

        texto_cliente = (
            f"Pagamento confirmado para o pedido {pedido.id}. Motoristas serão notificados em breve.\n"
            f"A central receberá o valor e repassará a comissão ao motorista após o serviço."
        )
        enviar_whatsapp_meta(sender, texto_cliente)
        notificacoes = _broadcast_to_drivers(db, pedido)
        return {"status": "pedido_pago", "pedido_id": pedido.id, "notificacoes": notificacoes}

    if "aceito" in lower or "aceitar" in lower:
        driver = db.query(models.Motorista).filter(
            models.Motorista.telefone == sender).first()
        if not driver:
            text = "Seu número não está cadastrado como motorista. Por favor, use o painel ou fale com o administrador."
            enviar_whatsapp_meta(sender, text)
            return {"status": "motorista_nao_cadastrado", "mensagem": text}

        order_id = _parse_order_id(lower)
        if not order_id:
            text = "Envie 'aceito pedido <id>' para aceitar um serviço específico."
            enviar_whatsapp_meta(sender, text)
            return {"status": "sem_id_pedido", "mensagem": text}

        pedido = db.query(models.Pedido).filter(  # Agora usando models.Pedido
            models.Pedido.id == order_id).first()
        if not pedido:
            text = f"Pedido {order_id} não encontrado."
            enviar_whatsapp_meta(sender, text)
            return {"status": "pedido_nao_encontrado", "mensagem": text}

        if pedido.motorista_id is not None:
            text = f"O pedido {order_id} já foi aceito por outro motorista."
            enviar_whatsapp_meta(sender, text)
            return {"status": "pedido_ja_aceito", "mensagem": text}

        if pedido.status == "AGUARDANDO_PAGAMENTO":
            text = f"O pedido {order_id} ainda aguarda pagamento. Peça ao cliente para confirmar o pagamento antes de aceitar."
            enviar_whatsapp_meta(sender, text)
            return {"status": "aguardando_pagamento", "mensagem": text}

        pedido.motorista_id = driver.id
        pedido.status = 'ACEITO'
        db.commit()
        db.refresh(pedido)
        # Alterado pedido.data para pedido.data_servico e adicionado formatação
        text_driver = f"Você aceitou o pedido {order_id}. Origem: {pedido.origem} Destino: {pedido.destino} Data: {pedido.data_servico} Valor: R$ {pedido.valor}."
        enviar_whatsapp_meta(sender, text_driver)

        if pedido.cliente.telefone:
            text_cliente = f"Seu pedido {order_id} foi aceito pelo motorista {driver.nome}. Em breve ele estará a caminho."
            enviar_whatsapp_meta(pedido.cliente.telefone, text_cliente)

        return {"status": "pedido_aceito", "pedido_id": order_id}

    if "concluido" in lower or "finalizado" in lower or "terminei" in lower:
        driver = db.query(models.Motorista).filter(
            models.Motorista.telefone == sender).first()
        if not driver:
            return {"status": "erro", "mensagem": "Apenas motoristas podem concluir pedidos."}

        order_id = _parse_order_id(lower)
        if not order_id:
            # Tenta buscar o último pedido aceito por este motorista que não esteja concluído
            pedido = db.query(models.Pedido).filter(  # Agora usando models.Pedido
                models.Pedido.motorista_id == driver.id,
                models.Pedido.status == 'ACEITO'
            ).order_by(models.Pedido.id.desc()).first()
        else:
            pedido = db.query(models.Pedido).filter(
                models.Pedido.id == order_id).first()

        if not pedido or pedido.motorista_id != driver.id:
            text = "Não encontrei um pedido em andamento sob sua responsabilidade para finalizar."
            enviar_whatsapp_meta(sender, text)
            return {"status": "erro", "mensagem": text}

        pedido.status = 'CONCLUIDO'
        db.commit()

        text_driver = f"Parabéns! Pedido {pedido.id} finalizado com sucesso. A comissão será processada pela central."
        enviar_whatsapp_meta(sender, text_driver)

        if pedido.cliente.telefone:
            text_cliente = (
                f"Seu transporte (Pedido {pedido.id}) foi finalizado. "
                "Obrigado por escolher a Central Transfers! Esperamos vê-lo em breve."
            )
            enviar_whatsapp_meta(pedido.cliente.telefone, text_cliente)

        return {"status": "pedido_concluido", "pedido_id": pedido.id}

    service_name, service_type = _guess_service(message)
    origem = _parse_field(message, "origem:")
    destino = _parse_field(message, "destino:")
    data_servico = _parse_date(message)
    valor = _parse_price(message)

    try:
        if not service_name or not origem or not destino:
            help_text = (
                "Por favor envie a mensagem com os dados do pedido: serviço, origem, destino, data e valor. "
                "Exemplo: 'Pedido transfer origem: aeroporto destino: hotel data: 16/04/2026 12:00 valor: 180'."
            )
            enviar_whatsapp_meta(sender, help_text)
            return {"status": "aguardando_informacoes", "mensagem": help_text}

        cliente = _find_or_create_client(db, sender)
        servico = _find_or_create_service(db, service_name, service_type)

        novo_pedido = models.Pedido(  # Agora usando models.Pedido
            cliente_id=cliente.id,
            servico_id=servico.id,
            origem=origem,
            destino=destino,
            data_servico=data_servico,
            valor=valor,
            observacoes=message,
            status="AGUARDANDO_PAGAMENTO"  # Padronizado para o Painel
        )
        db.add(novo_pedido)
        db.commit()
        db.refresh(novo_pedido)

        mensagem_retorno = (
            f"Recebemos seu pedido {service_name}. Use {PAYMENT_METHOD} para pagar o serviço e envie 'pago pedido {novo_pedido.id}' após a transferência.\n"
            f"Dados da central:\n{CENTRAL_BANK_DETAILS}\n{COMMISSION_NOTE}"
        )
        enviar_whatsapp_meta(sender, mensagem_retorno)
        return {"status": "pedido_criado", "pedido_id": novo_pedido.id}
    except Exception as e:
        logger.error(f"Erro ao processar pedido via WhatsApp: {e}")
        db.rollback()
        return {"status": "erro_interno", "detalhe": str(e)}
