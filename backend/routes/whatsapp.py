import os
import json
from datetime import datetime
import re
import urllib.parse
import logging
import hmac
import hashlib

from fastapi import APIRouter, HTTPException, Query, Response, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from typing import Optional

from backend import models
from backend.config import settings
from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.database import SessionLocal
from backend.services.pagamento_service import criar_checkout_pro
from backend.auth import hash_senha
from backend.services.email_service import notificar_cliente_motorista_atribuido

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SERVICE_MAP = {
    "gramado": ("Tour Gramado", "Tour"),
    "uva": ("Tour Uva e Vinho", "Tour"),
    "vinho": ("Tour Uva e Vinho", "Tour"),
    "bento": ("Bento Gonçalves", "Tour"),
    "disposicao": ("Carro a disposição", "Carro à disposição"),
    "transfer": ("Transfer", "Transfer"),
}

BOOKING_KEYWORDS = ["pedido", "reserva",
                    "transfer", "tour", "viagem", "origem"]

PAYMENT_METHOD = "PIX ou transferência bancária"

CENTRAL_BANK_DETAILS = (
    "R.DE S.ROCHA LTDA\n"
    "Banco: 336 - C6 S.A.\n"
    "Agência: 0001\n"
    "Conta: 35224666-9\n"
    "PIX: 58.011.293/0001-92\n"
)

COMMISSION_NOTE = "A central recebe o valor e repassa a comissão após a viagem."


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
    end = len(remainder)

    for sep in ["\n", ";", ".", ","]:
        pos = remainder.find(sep)
        if pos != -1:
            end = min(end, pos)

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

    if "hoje" in raw.lower():
        return datetime.now()

    raw = raw.replace(" às ", " ").replace(" as ", " ").replace("h", ":")

    formatos = [
        "%Y-%m-%dT%H:%M",
        "%d/%m/%Y %H:%M",
        "%d/%m/%y %H:%M",
        "%d/%m %H:%M",
        "%d/%m/%Y",
        "%Y-%m-%d %H:%M",
    ]

    for fmt in formatos:
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue

        return datetime.now()


def _parse_order_id(message: str):
    match = re.search(r"pedido\s*#?\s*(\d+)", message.lower())
    return int(match.group(1)) if match else None

    # =========================
    # WEBHOOK VERIFICATION
    # =========================


@router.get("/incoming")
def whatsapp_verify(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):

    print("MODE:", mode)
    print("TOKEN RECEBIDO:", repr(token))
    print("TOKEN ESPERADO:", repr(settings.WHATSAPP_VERIFY_TOKEN))

    # Verificação oficial para o handshake da Meta (corrigido)
    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:  # Removed syntax error
        logger.info("✅ Webhook verificado com sucesso pelo Meta.")
        return Response(content=challenge, media_type="text/plain")

    logger.warning(
        f"❌ Falha na verificação do Webhook. Token esperado: {settings.WHATSAPP_VERIFY_TOKEN}")
    return Response(content="forbidden", status_code=403)

# =========================
# WEBHOOK PRINCIPAL
# =========================


@router.post("/incoming")
async def whatsapp_incoming(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers.get("X-Hub-Signature-256")

    # Validação de Assinatura HMAC (Só ativa se o SECRET estiver configurado no .env)
    if settings.WHATSAPP_APP_SECRET and signature and settings.ENV != "development":
        body = await request.body()
        expected = hmac.new(
            settings.WHATSAPP_APP_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature.replace("sha256=", ""), expected):
            return Response(status_code=403)

    # Processamento do Payload
    try:
        data = await request.json()
        sender = None
        message = None

        # Extração inteligente: Funciona para Meta Oficial e para seu Script de Simulação
        if "entry" in data:
            try:
                msg_obj = data["entry"][0]["changes"][0]["value"]["messages"][0]
                sender = msg_obj.get("from")
                message = msg_obj.get("text", {}).get("body")
            except (KeyError, IndexError):
                return {"status": "ignored", "reason": "non_message_event"}
        else:
            sender = data.get("sender") or data.get("from")
            message = data.get("message") or data.get("text", {}).get("body")

        if not sender:
            return {"status": "error", "message": "sender_not_found"}

        logger.info(f"📩 Mensagem de {sender}: {message}")
        background_tasks.add_task(processar_evento_whatsapp, {"sender": sender, "message": message})
        return {"status": "accepted"}

    except Exception as e:
        logger.error(f"Erro ao processar webhook WhatsApp: {e}", exc_info=True)
        # Retornamos 202 para a Meta não tentar reenviar infinitamente um erro de código
        return Response(status_code=202)

        # =========================
        # BACKGROUND PROCESSING
        # =========================


def processar_evento_whatsapp(data: dict):
    db = SessionLocal()
    try:
        _executar_logica_negocio_whatsapp(data, db)
    finally:
        db.close()


def _executar_logica_negocio_whatsapp(data: dict, db: Session):
    # Tenta extrair do formato aninhado da Meta ou do formato simples
    sender = data.get("from") or data.get("sender")
    message = data.get("message")

    if "entry" in data:
        try:
            val = data["entry"][0]["changes"][0]["value"]["messages"][0]
            sender = val.get("from")
            message = val.get("text", {}).get("body")
        except (KeyError, IndexError):
            pass

    if not sender:
        return

    lower = str(message).lower() if message else ""

    # exemplo mínimo (mantive sua lógica original fora para evitar quebra)
    if "pago" in lower:
        enviar_whatsapp_meta(sender, "Pagamento recebido.")
        return

    if "aceito" in lower:
        enviar_whatsapp_meta(sender, "Pedido aceito.")
        return

    enviar_whatsapp_meta(sender, "Mensagem recebida.")


def broadcast_to_drivers(db: Session, pedido: models.Pedido):
    motoristas = db.query(models.Motorista).filter(
        models.Motorista.telefone.isnot(None),
        models.Motorista.status == "ATIVO"
    ).all()

    mensagens = []

    for motorista in motoristas:
        try:
            texto = (
                f"🚖 Novo pedido #{pedido.id}\n"
                f"📍 {pedido.origem} → {pedido.destino}\n"
                f"📅 {pedido.data_servico.strftime('%d/%m/%Y %H:%M')}\n"
                f"💰 R$ {pedido.valor}\n\n"
                f"Responda: aceitar pedido {pedido.id}"
            )

            status, resp = enviar_whatsapp_meta(
                motorista.telefone,
                texto
            )

            mensagens.append({
                "motorista": motorista.id,
                "status": status,
                "response": resp
            })

        except Exception as e:
            logger.error(f"Erro motorista {motorista.id}: {e}")

            return mensagens
