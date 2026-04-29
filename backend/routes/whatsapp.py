from datetime import datetime
import re
import logging
from fastapi import APIRouter, HTTPException, Query, Depends, Response, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from typing import Optional
from backend import models, schemas
from backend.config import settings
from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.database import get_db, SessionLocal
from backend.services.pagamento_service import criar_checkout_pro
from backend.auth import hash_senha
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

    # Melhoria: Suporte a palavras-chave simples
    if raw and "hoje" in raw.lower():
        return datetime.now()

    if not raw:
        return datetime.now()

    raw = raw.replace(" às ", " ").replace(" as ", " ").replace("h", ":")

    formatos = [
        "%Y-%m-%dT%H:%M", "%d/%m/%Y %H:%M", "%d/%m/%y %H:%M",
        "%d/%m %H:%M", "%d/%m/%Y", "%Y-%m-%d %H:%M", "%d-%m-%Y %H:%M"
    ]
    for fmt in formatos:
        try:
            dt = datetime.strptime(raw, fmt)
            # type: ignore
            return dt.replace(year=datetime.now().year) if dt.year == 1900 else dt
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

    # Melhoria: Usar um segredo mais forte ou gerar UUID para senhas de contas automáticas
    import secrets
    senha_aleatoria = secrets.token_urlsafe(16)

    novo_usuario = models.Usuario(
        email=email_simulado, senha=hash_senha(senha_aleatoria))
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
    cliente = db.query(models.Cliente).filter(
        models.Cliente.telefone == phone).first()
    if cliente:
        return cliente

    # Tenta criar um nome amigável a partir do telefone
    nome_cliente = f"Cliente via WhatsApp ({phone[-4:]})"

    novo_cliente = models.Cliente(nome=nome_cliente, telefone=phone)
    db.add(novo_cliente)
    db.flush()  # Usa flush para obter o ID antes do commit final
    db.commit()
    db.refresh(novo_cliente)
    return novo_cliente


def broadcast_to_drivers(db: Session, pedido: models.Pedido):
    motoristas = db.query(models.Motorista).filter(
        models.Motorista.telefone.isnot(None),
        models.Motorista.status == 'ATIVO'
    ).all()
    mensagens = []
    for motorista in motoristas:
        try:
            # Configuração do botão interativo para o motorista
            interactive_payload = {
                "type": "button",
                "body": {
                    "text": (
                        f"🚖 *Novo Pedido #{pedido.id}*\n"
                        f"📍 Origem: {pedido.origem}\n🏁 Destino: {pedido.destino}\n"
                        f"📅 Data: {pedido.data_servico.strftime('%d/%m/%Y %H:%M')}\n\n"
                        "Deseja aceitar este serviço?"
                    )
                },
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {
                            "id": f"ACEITAR_PEDIDO_{pedido.id}", "title": "Aceitar ✅"}}
                    ]
                }
            }

            status_code, response = enviar_whatsapp_meta(
                motorista.telefone,
                "",  # Mensagem de texto vazia pois usaremos o payload interativo
                payload_interativo=interactive_payload
            )
            mensagens.append({"telefone": motorista.telefone,
                             "status": status_code, "response": response})
        except Exception as e:
            logger.error(f"Falha ao notificar motorista {motorista.id}: {e}")
            continue
    return mensagens


def processar_evento_whatsapp(data: dict):
    """
    Tarefa executada em segundo plano para não bloquear a resposta do webhook.
    Gerencia sua própria sessão de banco de dados.
    """
    db = SessionLocal()
    try:
        # Lógica de extração e processamento movida para cá
        _executar_logica_negocio_whatsapp(data, db)
    except Exception as e:
        logger.error(
            f"💥 Erro no processamento assíncrono do WhatsApp: {e}", exc_info=True)
    finally:
        db.close()


def _executar_logica_negocio_whatsapp(data: dict, db: Session):
    """
    Contém a lógica de parsing e regras de negócio que antes estava na rota.
    """
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
            sender = data.get("sender")
            message = data.get("message")
    except (KeyError, IndexError):
        return

    if not sender or not message:
        return

    # Sanitização básica de entrada
    message = "".join(char for char in message if char.isprintable())
    message = message.strip()
    lower = message.lower()

    # Tratamento seguro para respostas de botões interativos
    try:
        if "entry" in data:
            msg_obj = data["entry"][0]["changes"][0]["value"]["messages"][0]
            if msg_obj.get("type") == "interactive":
                interactive_response = msg_obj["interactive"]["button_reply"]["id"]
                logger.info(f"Botão clicado: {interactive_response}")

                if interactive_response and interactive_response.startswith("ACEITAR_PEDIDO_"):
                    order_id = int(interactive_response.replace(
                        "ACEITAR_PEDIDO_", ""))
                    lower = f"aceito pedido {order_id}"
        elif data.get("interactive_id"):  # Fallback para simuladores simplificados
            interactive_id = data.get("interactive_id")
            if interactive_id.startswith("ACEITAR_PEDIDO_"):
                order_id = int(interactive_id.replace("ACEITAR_PEDIDO_", ""))
                lower = f"aceito pedido {order_id}"
    except (KeyError, IndexError, TypeError):
        pass

    logger.info(
        f"[WHATSAPP RECEBIDO] Remetente: {sender} | Conteúdo Final: {lower}")

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
                models.Pedido.status.in_(['AGUARDANDO_PAGAMENTO', 'PENDENTE']),
                models.Pedido.data_servico >= datetime.now()  # Apenas pedidos futuros
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
        notificacoes = broadcast_to_drivers(db, pedido)
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

        # Melhoria: Formatação amigável da data para o motorista
        data_formatada = pedido.data_servico.strftime('%d/%m/%Y %H:%M')
        text_driver = (
            f"✅ Você aceitou o pedido #{order_id}!\n\n"
            f"📍 Origem: {pedido.origem}\n🏁 Destino: {pedido.destino}\n📅 Data: {data_formatada}\n💰 Valor: R$ {pedido.valor}"
        )
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

    if "cancelar" in lower or "cancela" in lower:
        order_id = _parse_order_id(lower)
        if not order_id:
            enviar_whatsapp_meta(
                sender, "Por favor, informe o ID do pedido. Ex: 'cancelar pedido 123'")
            return {"status": "erro", "mensagem": "ID não informado"}

        pedido = db.query(models.Pedido).filter(
            models.Pedido.id == order_id).first()
        if not pedido:
            enviar_whatsapp_meta(sender, f"Pedido {order_id} não encontrado.")
            return {"status": "erro"}

        if pedido.status == "CONCLUIDO":
            enviar_whatsapp_meta(
                sender, "Este pedido já foi concluído e não pode ser cancelado.")
            return {"status": "erro"}

        # Verifica se quem cancela é o cliente ou o motorista do pedido
        is_cliente = pedido.cliente.telefone == sender
        is_motorista = pedido.motorista and pedido.motorista.telefone == sender

        if not (is_cliente or is_motorista):
            enviar_whatsapp_meta(
                sender, "Você não tem permissão para cancelar este pedido.")
            return {"status": "permissao_negada"}

        pedido.status = "CANCELADO"
        db.commit()

        msg_confirmacao = f"❌ O pedido #{order_id} foi cancelado com sucesso."
        enviar_whatsapp_meta(sender, msg_confirmacao)

        # Notifica a outra parte
        if is_cliente and pedido.motorista:
            enviar_whatsapp_meta(
                pedido.motorista.telefone,
                f"⚠️ O cliente cancelou o pedido #{order_id} ({pedido.origem} -> {pedido.destino})."
            )
        elif is_motorista and pedido.cliente:
            enviar_whatsapp_meta(
                pedido.cliente.telefone,
                f"⚠️ O motorista não poderá realizar o seu pedido #{order_id}. Entre em contato com a central para novo agendamento."
            )
        return {"status": "pedido_cancelado", "id": order_id}

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

        # Define 20% como taxa da central
        comissao_calculada = float(valor) * 0.20

        novo_pedido = models.Pedido(  # Agora usando models.Pedido
            cliente_id=cliente.id,
            servico_id=servico.id,
            origem=origem,
            destino=destino,
            data_servico=data_servico,
            valor=valor,
            valor_comissao=comissao_calculada,
            observacoes=message,
            status="AGUARDANDO_PAGAMENTO"  # Padronizado para o Painel
        )
        db.add(novo_pedido)
        db.commit()
        db.refresh(novo_pedido)

        # Fluxo de Checkout Pro (PROD)
        try:
            checkout_url = criar_checkout_pro(
                novo_pedido.id, novo_pedido.valor)
            instrucao_pagamento = (
                f"Para finalizar sua reserva, realize o pagamento no link abaixo:\n\n"
                f"{checkout_url}\n\n"
                "Você pode pagar via PIX ou Cartão. O sistema liberará seu pedido automaticamente após a confirmação."
            )
        except Exception as e:
            logger.error(f"Erro ao gerar Checkout: {e}")
            instrucao_pagamento = f"Erro ao gerar link de pagamento. Por favor, use nossos dados bancários:\n{CENTRAL_BANK_DETAILS}"

        mensagem_retorno = (
            f"✅ Recebemos seu pedido {service_name} (#{novo_pedido.id}).\n\n"
            f"{instrucao_pagamento}\n\n{COMMISSION_NOTE}"
        )
        enviar_whatsapp_meta(sender, mensagem_retorno)
        return {"status": "pedido_criado", "pedido_id": novo_pedido.id}
    except Exception as e:
        logger.error(f"💥 Erro ao processar lógica de negócio do WhatsApp: {e}")
        db.rollback()
        raise e
