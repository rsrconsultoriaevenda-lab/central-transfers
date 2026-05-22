import json
import logging
import re
import hmac
import hashlib

from datetime import datetime
from decimal import Decimal

from fastapi import (
    APIRouter,
    Query,
    Response,
    Request,
    BackgroundTasks,
    Depends,
)

from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend import models
from backend.config import settings
from backend.database import SessionLocal, get_db
from backend.services.whatsapp_service import enviar_whatsapp_meta

router = APIRouter(
    prefix="/whatsapp",
    tags=["WhatsApp"]
)

logger = logging.getLogger(__name__)

# =========================
# MAPA DE SERVIÇOS
# =========================

SERVICE_MAP = {
    "gramado": ("Tour Gramado", "Tour"),
    "uva": ("Tour Uva e Vinho", "Tour"),
    "vinho": ("Tour Uva e Vinho", "Tour"),
    "bento": ("Bento Gonçalves", "Tour"),
    "disposicao": ("Carro a disposição", "Carro à disposição"),
    "transfer": ("Transfer", "Transfer"),
}

# =========================
# UTILITÁRIOS
# =========================


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

    seps = ["\n", ";", ".", ","]
    pos_list = [remainder.find(s) for s in seps if remainder.find(s) != -1]
    if pos_list:
        return _clean_text(remainder[:min(pos_list)])
    return _clean_text(remainder)


def _guess_service(message: str):

    lower = message.lower()

    for key, (name, tipo) in SERVICE_MAP.items():

        if key in lower:
            return name, tipo

    return "Transfer", "Transfer"


def _parse_price(message: str):

    match = re.search(
        r"valor\s*[:\-]?\s*([0-9]+[\.,]?[0-9]*)",
        message.lower()
    )

    if match:
        return float(match.group(1).replace(",", "."))

    return 0.0


def _parse_date(message: str):

    raw = (
        _parse_field(message, "data:")
        or _parse_field(message, "em:")
    )

    if not raw or "hoje" in raw.lower():
        return datetime.now()

    raw = raw.replace(" às ", " ")
    raw = raw.replace(" as ", " ")
    raw = raw.replace("h", ":")

    formatos = [
        "%d/%m/%Y %H:%M",
        "%d/%m/%y %H:%M",
        "%d/%m %H:%M",
        "%Y-%m-%d %H:%M"
    ]

    for fmt in formatos:
        try:
            dt = datetime.strptime(raw, fmt)
            if dt.year == 1900:
                dt = dt.replace(year=datetime.now().year)
            return dt

        except ValueError:
            continue

    return datetime.now()


def _parse_order_id(message: str):

    match = re.search(
        r"pedido\s*#?\s*(\d+)",
        message.lower()
    )

    return int(match.group(1)) if match else None

# =========================
# WEBHOOK VERIFY
# =========================


@router.get("/webhook")
async def whatsapp_verify(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):

    verify_token = getattr(
        settings,
        "WHATSAPP_VERIFY_TOKEN",
        None
    )

    logger.info(f"Handshake recebido - mode={mode}")

    if (
        mode == "subscribe"
        and token == verify_token
        and verify_token is not None
    ):

        logger.info("Webhook validado com sucesso")

        return PlainTextResponse(content=challenge)

    logger.warning("Falha na validação do webhook")

    return Response(
        content="Forbidden",
        status_code=403
    )


# =========================
# WEBHOOK PRINCIPAL
# =========================

@router.post("/webhook")
async def whatsapp_incoming(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):

    signature = request.headers.get(
        "X-Hub-Signature-256"
    )

    body = await request.body()

    app_secret = getattr(settings, "WHATSAPP_APP_SECRET", None)
    env = getattr(settings, "ENV", "development")

    # 1. Validação de Assinatura (Apenas em Produção)
    if app_secret and signature and env == "production":
        expected = hmac.new(
            app_secret.encode(),
            body,
            hashlib.sha256
        ).hexdigest()
        received = signature.replace("sha256=", "")
        if not hmac.compare_digest(received, expected):
            logger.warning("Assinatura inválida")
            return Response(status_code=403)

    # 2. Processamento da Mensagem (Dev e Produção Validada)
    status = "ignored"
    try:
        data = json.loads(body)
        if "entry" not in data:
            return {"status": status}

        try:
            # Extração segura dos campos da Meta Cloud API
            entry = data["entry"][0]
            changes = entry.get("changes", [{}])[0].get("value", {})

            if "messages" in changes:
                msg_obj = changes["messages"][0]
                sender = msg_obj.get("from")
                message_text = msg_obj.get("text", {}).get("body")
                interactive = msg_obj.get("interactive", {})
                button_reply = interactive.get("button_reply", {})

                if not sender:
                    status = "no_sender"
                elif button_reply.get("id"):
                    status = "botao_processado"
                elif message_text:
                    lower_text = message_text.strip().lower()
                    if lower_text == "oi" or lower_text.startswith("oi") or lower_text.startswith("olá"):
                        status = "saudacao"
                    elif "vagas" in lower_text:
                        status = "vagas_listadas"
                    else:
                        status = "received"

                if sender and (message_text or button_reply):
                    logger.info(
                        f"📱 WhatsApp de {sender}: {message_text or button_reply}")

                    notifier = getattr(request.app.state, "notifier", None)
                    background_tasks.add_task(
                        processar_evento_whatsapp,
                        {
                            "sender": sender,
                            "message": message_text or ""
                        },
                        notifier
                    )

        except (KeyError, IndexError) as e:
            logger.debug(
                f"Evento WhatsApp ignorado ou formato desconhecido: {e}")

    except Exception as e:
        logger.error(f"Erro crítico no webhook: {e}")
        status = "error"

    # Retorna JSON para testes internos, mantendo status 200 para a Meta
    return {"status": status}


# =========================
# PROCESSAMENTO PRINCIPAL
# =========================


async def processar_evento_whatsapp(
    data: dict,
    notifier=None
):
    # CRÍTICO: Background tasks precisam de sua própria sessão.
    # Se usarmos a injetada pelo Depends, o FastAPI a fecha antes da task terminar.
    db = SessionLocal()
    try:
        sender = data.get("sender")
        message = data.get("message", "")

        lower = message.lower()

        # =========================
        # ACEITE DE PEDIDO
        # =========================

        # ACEITE DE PEDIDO
        if "aceitar pedido" in lower or "aceito pedido" in lower:
            pedido_id = _parse_order_id(message)
            if not pedido_id:
                return

            motorista = db.query(models.Motorista).filter(
                models.Motorista.telefone == sender).first()
            if not motorista:
                enviar_whatsapp_meta(sender, "❌ Telefone não cadastrado.")
                return

            # Validação de plano mensal (Replicado de pedidos.py)
            if motorista.plano == "MENSAL":
                inicio_mes = datetime.now().replace(
                    day=1, hour=0, minute=0, second=0, microsecond=0
                )
                contagem_mes = db.query(models.Pedido).filter(
                    models.Pedido.motorista_id == motorista.id,
                    models.Pedido.status.in_(["ACEITO", "CONCLUIDO"]),
                    models.Pedido.data_servico >= inicio_mes
                ).count()

                if contagem_mes >= 5:
                    enviar_whatsapp_meta(
                        sender,
                        "❌ Limite de 5 serviços mensais atingido no seu plano. "
                        "Acesse o painel para fazer o upgrade."
                    )
                    return

            pedido = db.query(models.Pedido).filter(
                models.Pedido.id == pedido_id,
                models.Pedido.status == "PENDENTE"
            ).with_for_update().first()

            if pedido:
                pedido.motorista_id = motorista.id
                pedido.status = "ACEITO"
                pedido.calcular_financeiro()
                db.commit()
                enviar_whatsapp_meta(sender, f"✅ Pedido #{pedido_id} aceito.")
                if pedido.cliente:
                    enviar_whatsapp_meta(
                        pedido.cliente.telefone, f"🚖 Motorista {motorista.nome} aceitou seu pedido.")
            else:
                enviar_whatsapp_meta(sender, "❌ Pedido indisponível.")

        # NOVO PEDIDO
        elif any(k in lower for k in ["pedido", "reserva", "transfer"]):
            origem = _parse_field(message, "origem:")
            destino = _parse_field(message, "destino:")

            if not origem or not destino:
                enviar_whatsapp_meta(
                    sender, "⚠️ Formato: Pedido origem: X destino: Y")
                return

            cliente = db.query(models.Cliente).filter(
                models.Cliente.telefone == sender).first()
            if not cliente:
                cliente = models.Cliente(
                    nome="Cliente WhatsApp", telefone=sender)
                db.add(cliente)
                db.flush()

            serv_nome, _ = _guess_service(message)
            servico = db.query(models.Servico).filter(
                models.Servico.nome == serv_nome).first()
            if not servico:
                servico = db.query(models.Servico).first()

            novo_pedido = models.Pedido(
                cliente=cliente,
                servico=servico,
                origem=origem,
                destino=destino,
                data_servico=_parse_date(message),
                valor=Decimal(str(_parse_price(message))),
                status="PENDENTE",
                canal_venda="whatsapp"
            )
            novo_pedido.calcular_financeiro()
            db.add(novo_pedido)
            db.commit()
            db.refresh(novo_pedido)

            enviar_whatsapp_meta(
                sender, f"✅ Pedido #{novo_pedido.id} recebido.")

            if notifier:
                await notifier.broadcast({
                    "type": "NEW_ORDER",
                    "pedido_id": novo_pedido.id,
                    "mensagem": f"Novo pedido: {origem} → {destino}",
                    "valor": str(novo_pedido.valor)
                })

            broadcast_to_drivers(db, novo_pedido)

    except Exception as e:

        logger.error(
            f"Erro processando evento: {e}"
        )
    finally:
        db.close()

        # =========================
        # BROADCAST MOTORISTAS
        # =========================


def broadcast_to_drivers(
    db: Session,
    pedido: models.Pedido
):

    motoristas = (
        db.query(models.Motorista)
        .filter(
            models.Motorista.status == "ATIVO"
        )
        .all()
    )

    texto = (
        f"🚖 *NOVO PEDIDO #{pedido.id}*\n"
        f"📍 {pedido.origem} → {pedido.destino}\n"
        f"📅 "
        f"{pedido.data_servico.strftime('%d/%m/%Y %H:%M')}\n"
        f"💰 R$ {pedido.valor}\n\n"
        f"Responda:\n"
        f"*aceitar pedido {pedido.id}*"
    )

    for motorista in motoristas:

        if motorista.telefone:

            enviar_whatsapp_meta(
                motorista.telefone,
                texto
            )
