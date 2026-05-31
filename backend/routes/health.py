import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import logging
from datetime import datetime

from backend.database import get_db
from backend import models
from backend.config import settings

router = APIRouter(prefix="/health", tags=["Health Check"])
logger = logging.getLogger(__name__)


@router.get("")
def health_check(request: Request, db: Session = Depends(get_db)):
    db_status = "OK"
    meta_api_status = "OK"
    overall_status = "OK"
    cors_status = "OK"
    ws_status = "OK"
    errors = []

    frontend_url = os.getenv("FRONTEND_URL", "Não configurada")

    # 1. Check Database Connection
    try:
        # Verifica a conexão e a existência da tabela principal
        db.execute(text("SELECT 1 FROM usuarios LIMIT 1")).fetchone()
        user_count = db.query(func.count(models.Usuario.id)).scalar()
        service_count = db.query(func.count(models.Servico.id)).scalar()
        db_info = {
            "status": "OK",
            "usuarios": user_count,
            "servicos": service_count
        }
    except Exception as e:
        db_status = "ERROR (Tables missing or connection failed)"
        db_info = {"status": "ERROR", "detail": str(e)}
        overall_status = "DEGRADED"
        errors.append(f"Database connection failed: {e}")
        logger.error(f"Health check DB error: {e}")

    # 2. Check Meta API Configuration (Sem request externo para evitar timeout)
    meta_api_status = "NOT_CONFIGURED"
    try:
        whatsapp_token = getattr(settings, "WHATSAPP_TOKEN", None)
        whatsapp_phone_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", None)

        if whatsapp_token and whatsapp_phone_id and "cole_seu" not in whatsapp_token:
            meta_api_status = "CONFIGURED"
        elif not whatsapp_token:
            meta_api_status = "DISABLED (PWA_ONLY)"

    except Exception as e:
        meta_api_status = f"ERROR: {str(e)}"

    # 3. Check CORS Security
    if getattr(settings, "ALLOWED_ORIGINS", "*") == "*":
        cors_status = "WARNING (Too Open)"
        env = getattr(settings, "ENV", os.getenv("ENV", "development"))
        if env == "production":
            errors.append(
                "CORS está configurado como '*' em produção. Isso é um risco de segurança.")

    # 4. Check Mercado Pago Connection (Opcional, mas recomendado)
    mp_status = "OK"
    try:
        if not settings.MERCADO_PAGO_ACCESS_TOKEN:
            mp_status = "WARNING"
        else:
            # Apenas valida se o token é aceito pela API de usuários do MP
            mp_url = "https://api.mercadopago.com/v1/me"
            mp_resp = requests.get(mp_url, headers={
                                   "Authorization": f"Bearer {settings.MERCADO_PAGO_ACCESS_TOKEN}"}, timeout=2)
            if mp_resp.status_code != 200:
                mp_status = "INVALID_TOKEN"
    except Exception:
        mp_status = "OFFLINE"

    # 5. Check WebSocket Notifier (Real-time Communication)
    notifier = getattr(request.app.state, "notifier", None)
    active_connections = 0
    ws_status = "OK"
    if not notifier:
        ws_status = "CRITICAL (Required for PWA)"
        overall_status = "ERROR"
    else:
        active_connections = len(getattr(notifier, "active_connections", []))

    # 6. Check Email Config
    email_status = "OK" if getattr(
        settings, "SMTP_USER", None) else "NOT_CONFIGURED"

    response_data = {
        "status": overall_status,
        "environment": getattr(settings, "ENV", "development"),
        "database_connectivity": db_status,
        "database_stats": db_info,
        "meta_api": meta_api_status,
        "mercado_pago": mp_status,
        "websocket": ws_status,
        "active_ws_clients": active_connections,
        "email_service": email_status,
        "cors_policy": cors_status,
        "configured_frontend": frontend_url,
        "timestamp": datetime.now().isoformat()
    }
    if errors:
        response_data["errors"] = errors

    if overall_status == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=response_data)

    return response_data
