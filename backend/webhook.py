from fastapi import APIRouter, Request
from backend.config import settings

router = APIRouter(prefix="/webhook")


@router.get("")
def verify(hub_mode: str = None, hub_challenge: str = None, hub_verify_token: str = None):
    if hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    return "Invalid token"


@router.post("")
async def receive_update(request: Request):
    data = await request.json()
    print("EVENTO WHATSAPP:", data)
    return {"status": "received"}
