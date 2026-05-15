import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import logging
from datetime import datetime

from backend.database import get_db
from backend.config import settings

router = APIRouter(prefix="/health", tags=["Health Check"])
logger = logging.getLogger(__name__)


@router.get("/")
def health_check(db: Session = Depends(get_db)):
    db_status = "OK"
    meta_api_status = "OK"
    overall_status = "OK"
    cors_status = "OK"
    errors = []
    frontend_url = os.getenv("FRONTEND_URL", "Não configurada")

    # 1. Check Database Connection
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = "ERROR"
        overall_status = "DEGRADED"
        errors.append(f"Database connection failed: {e}")
        logger.error(f"Health check DB error: {e}")

    # 2. Check Meta API Connection
    try:
        if not settings.WHATSAPP_TOKEN or not settings.WHATSAPP_PHONE_NUMBER_ID:
            meta_api_status = "WARNING"
            if overall_status == "OK":
                overall_status = "DEGRADED"
            errors.append("Meta API credentials not fully configured.")
        else:
            meta_api_url = f"https://graph.facebook.com/{settings.WHATSAPP_API_VERSION}/{settings.WHATSAPP_PHONE_NUMBER_ID}"
            headers = {"Authorization": f"Bearer {settings.WHATSAPP_TOKEN}"}

            response = requests.get(meta_api_url, headers=headers, timeout=5)
            response.raise_for_status()

            if "id" not in response.json():
                meta_api_status = "ERROR"
                overall_status = "ERROR"
                errors.append(
                    f"Meta API response missing expected 'id' field. Response: {response.text}")
                logger.error(
                    f"Health check Meta API response error: {response.text}")

    except requests.exceptions.Timeout:
        meta_api_status = "ERROR"
        overall_status = "ERROR"
        errors.append("Meta API request timed out.")
        logger.error("Health check Meta API timeout.")
    except requests.exceptions.RequestException as e:
        meta_api_status = "ERROR"
        overall_status = "ERROR"
        errors.append(f"Meta API connection failed: {e}")
        logger.error(f"Health check Meta API error: {e}")
    except Exception as e:
        meta_api_status = "ERROR"
        overall_status = "ERROR"
        errors.append(f"Unexpected error checking Meta API: {e}")
        logger.error(f"Health check Meta API unexpected error: {e}")

    # 3. Check CORS Security
    if settings.ALLOWED_ORIGINS == "*":
        cors_status = "WARNING (Too Open)"
        if settings.ENV == "production":
            errors.append(
                "CORS está configurado como '*' em produção. Isso é um risco de segurança.")

    # 3. Check Mercado Pago Connection (Opcional, mas recomendado)
    mp_status = "OK"
    try:
        if not settings.MERCADO_PAGO_ACCESS_TOKEN:
            mp_status = "WARNING"
        else:
            # Apenas valida se o token é aceito pela API de usuários do MP
            mp_url = "https://api.mercadopago.com/v1/me"
            mp_resp = requests.get(mp_url, headers={
                                   "Authorization": f"Bearer {settings.MERCADO_PAGO_ACCESS_TOKEN}"}, timeout=5)
            if mp_resp.status_code != 200:
                mp_status = "INVALID_TOKEN"
    except Exception:
        mp_status = "OFFLINE"

    response_data = {
        "status": overall_status,
        "database": db_status,
        "meta_api": meta_api_status,
        "mercado_pago": mp_status,
        "cors_policy": cors_status,
        "configured_frontend": frontend_url,
        "timestamp": datetime.now().isoformat(),
    }
    if errors:
        response_data["errors"] = errors

    if overall_status == "ERROR":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=response_data)

    return response_data
