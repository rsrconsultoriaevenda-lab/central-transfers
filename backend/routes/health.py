import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from datetime import datetime

from backend.database import get_db
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
    except Exception as e:
        db_status = "ERROR (Tables missing or connection failed)"
        overall_status = "DEGRADED"
        errors.append(f"Database connection failed: {e}")
        logger.error(f"Health check DB error: {e}")

    # 2. Check Meta API Connection
    try:
        whatsapp_token = getattr(settings, "WHATSAPP_TOKEN", None)
        whatsapp_phone_id = getattr(settings, "WHATSAPP_PHONE_NUMBER_ID", None)
        whatsapp_api_version = getattr(
            settings, "WHATSAPP_API_VERSION", "v20.0")

        if not whatsapp_token or not whatsapp_phone_id:
            meta_api_status = "DISABLED (PWA Active)"
        else:
            meta_api_url = f"https://graph.facebook.com/{whatsapp_api_version}/{whatsapp_phone_id}"
            headers = {"Authorization": f"Bearer {whatsapp_token}"}

            # Reduzimos o timeout para 2s para não travar a resposta do nosso sistema
            response = requests.get(meta_api_url, headers=headers, timeout=2)
            response.raise_for_status()

            if "id" not in response.json():
                meta_api_status = "ERROR"
                errors.append(
                    f"Meta API response missing expected 'id' field. Response: {response.text}")
                logger.error(
                    f"Health check Meta API response error: {response.text}")

    except requests.exceptions.Timeout:
        meta_api_status = "TIMEOUT (Ignored)"
        errors.append("Meta API request timed out.")
        logger.error("Health check Meta API timeout.")
    except requests.exceptions.RequestException as e:
        meta_api_status = "OFFLINE (Ignored)"
        errors.append(f"Meta API connection failed: {e}")
        logger.error(f"Health check Meta API error: {e}")
    except Exception as e:
        meta_api_status = "ERROR"
        errors.append(f"Unexpected error checking Meta API: {e}")
        logger.error(f"Health check Meta API unexpected error: {e}")

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
        "database": db_status,
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
