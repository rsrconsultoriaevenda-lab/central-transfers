from fastapi import APIRouter, Request
from fastapi.responses import PlainTextResponse
from backend.config import settings

router = APIRouter(prefix="/webhook")


@router.get("")
def verify(request: Request):
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)
    return PlainTextResponse(content="forbidden", status_code=403)


@router.post("")
async def receive_update(request: Request):
    data = await request.json()
    print("EVENTO WHATSAPP:", data)
    return {"status": "received"}
