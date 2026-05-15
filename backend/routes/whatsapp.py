import os
import json
from datetime import datetime
import re
import logging
import hmac
import hashlib
from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query, Response, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session

from backend import models
from backend.config import settings
from backend.services.whatsapp_service import enviar_whatsapp_meta
from backend.database import SessionLocal
from backend.auth import hash_senha

router = APIRouter(prefix="/whatsapp", tags=["WhatsApp"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mapeamento de serviços para facilitar o parsing
SERVICE_MAP = {
    "gramado": ("Tour Gramado", "Tour"),
    "uva": ("Tour Uva e Vinho", "Tour"),
    "vinho": ("Tour Uva e Vinho", "Tour"),
    "bento": ("Bento Gonçalves", "Tour"),
    "disposicao": ("Carro a disposição", "Carro à disposição"),
    "transfer": ("Transfer", "Transfer"),
}

# =========================
# UTILITÁRIOS DE PARSING
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
    return "Transfer", "Transfer"


def _parse_price(message: str):
    match = re.search(
        r"valor\s*[:\-]?\s*([0-9]+[\.,]?[0-9]*)", message.lower())
    if match:
        return float(match.group(1).replace(",", "."))
    return 0.0


def _parse_date(message: str):
    raw = _parse_field(message, "data:") or _parse_field(message, "em:")
    if not raw or "hoje" in raw.lower():
        return datetime.now()

    raw = raw.replace(" às ", " ").replace(" as ", " ").replace("h", ":")
    formatos = ["%d/%m/%Y %H:%M", "%d/%m/%y %H:%M",
                "%d/%m %H:%M", "%Y-%m-%d %H:%M"]

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
    match = re.search(r"pedido\s*#?\s*(\d+)", message.lower())
    return int(match.group(1)) if match else None

    # =========================
    # WEBHOOK VERIFICATION (GET)
    # =========================


@router.get("/webhook")
async def whatsapp_verify(
    mode: str = Query(None, alias="hub.mode"),
    token: str = Query(None, alias="hub.verify_token"),
    challenge: str = Query(None, alias="hub.challenge")
):
    """Handshake de verificação da Meta API."""
    verify_token = getattr(settings, "WHATSAPP_VERIFY_TOKEN", None)

    logger.info(f"🔍 Tentativa de Handshake - Mode: {mode}")

    if mode == "subscribe" and token == verify_token and verify_token is not None:
        logger.info("✅ Webhook verificado com sucesso!")
        return PlainTextResponse(content=challenge)

    logger.warning(f"❌ Falha no Handshake. Token recebido: {token}")
    return Response(content="Forbidden", status_code=403)

    # =========================
    # WEBHOOK PRINCIPAL (POST)
    # =========================


@router.post("/webhook")
async def whatsapp_incoming(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers.get("X-Hub-Signature-256")
    body = await request.body()

    # Validação HMAC (Segurança)
    if settings.WHATSAPP_APP_SECRET and signature and settings.ENV == "production":
        expected = hmac.new(
            settings.WHATSAPP_APP_SECRET.encode(),
            body,
            hashlib.sha256
        ).hexdigest()

        if not hmac.compare_digest(signature.replace("sha256=", ""), expected):
            logger.warning("🚫 Assinatura do WhatsApp inválida.")
            return Response(status_code=403)

    try:
        data = json.loads(body)

        # Extração Meta Oficial
        if "entry" in data:
            try:
                changes = data["entry"][0]["changes"][0]["value"]
                if "messages" in changes:
                    msg_obj = changes["messages"][0]
                    sender = msg_obj.get("from")
                    message = msg_obj.get("text", {}).get("body")

                    if sender and message:
                        logger.info(f"📩 Mensagem de {sender}: {message}")
                        # Passamos o notifier do estado da aplicação para a tarefa de fundo
                        notifier = getattr(request.app.state, "notifier", None)
                        background_tasks.add_task(
                            processar_evento_whatsapp,
                            {"sender": sender, "message": message},
                            notifier
                        )
            except (KeyError, IndexError):
                pass

        return {"status": "accepted"}

    except Exception as e:
        logger.error(f"Erro no processamento do webhook: {e}")
        # Meta exige 200 para não reenviar o erro
        return Response(status_code=200)

        # =========================
        # LÓGICA DE NEGÓCIO
        # =========================


def processar_evento_whatsapp(data: dict, notifier=None):
    db = SessionLocal()
    try:
        sender = data.get("sender")
        message = data.get("message", "")
        lower = message.lower()

        # 1. ACEITE DO MOTORISTA (Prioridade)
        if "aceitar pedido" in lower or "aceito pedido" in lower:
            pedido_id = _parse_order_id(message)
            if not pedido_id:
                return

            motorista = db.query(models.Motorista).filter(
                models.Motorista.telefone == sender).first()
            if not motorista:
                enviar_whatsapp_meta(
                    sender, "❌ Telefone não cadastrado como motorista.")
                return

            # LOCK: Evita corrida de dados (Race Condition)
            pedido = db.query(models.Pedido).filter(
                models.Pedido.id == pedido_id,
                models.Pedido.status == "PENDENTE"
            ).with_for_update().first()

            if pedido:
                pedido.motorista_id = motorista.id
                pedido.status = "ACEITO"
                enviar_whatsapp_meta(
                    sender, f"✅ Pedido #{pedido_id} é seu! Bom trabalho.")
                if pedido.cliente:
                    enviar_whatsapp_meta(
                        pedido.cliente.telefone, f"🚖 O motorista {motorista.nome} aceitou seu pedido!")
                db.commit()
            else:
                enviar_whatsapp_meta(
                    sender, "❌ Este pedido já foi aceito ou não está mais disponível.")

        # 2. CRIAÇÃO DE PEDIDO (Cliente)
        elif any(k in lower for k in ["pedido", "reserva", "transfer"]):
            origem = _parse_field(message, "origem:")
            destino = _parse_field(message, "destino:")

            if not origem or not destino:
                enviar_whatsapp_meta(
                    sender, "⚠️ Use o formato: Pedido origem: [Local] destino: [Local]")
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
                models.Servico.nome == serv_nome).first() or db.query(models.Servico).first()

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
            db.add(novo_pedido)
            db.commit()
            db.refresh(novo_pedido)

            enviar_whatsapp_meta(
                sender, f"✅ Pedido #{novo_pedido.id} recebido! Aguarde um motorista.")

            # 3. Notificação WebSocket (In-App)
            if notifier:
                import asyncio
                asyncio.create_task(notifier.notify_drivers({
                    "type": "NEW_ORDER",
                    "pedido_id": novo_pedido.id,
                    "mensagem": f"Novo pedido via WhatsApp: {origem} -> {destino}",
                    "valor": str(novo_pedido.valor)
                }))

            broadcast_to_drivers(db, novo_pedido)

    except Exception as e:
        logger.error(f"Erro na execução: {e}")
    finally:
        db.close()


def broadcast_to_drivers(db: Session, pedido: models.Pedido):
    motoristas = db.query(models.Motorista).filter(
        models.Motorista.status == "ATIVO").all()
    texto = (
        f"🚖 *NOVO PEDIDO #{pedido.id}*\n"
        f"📍 {pedido.origem} → {pedido.destino}\n"
        f"📅 {pedido.data_servico.strftime('%d/%m/%Y %H:%M')}\n"
        f"💰 R$ {pedido.valor}\n\n"
        f"Responda: *aceitar pedido {pedido.id}*"
    )
    for m in motoristas:
        if m.telefone:
            enviar_whatsapp_meta(m.telefone, texto)
