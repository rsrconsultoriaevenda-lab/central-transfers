from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import get_db
from backend.auth import get_usuario_atual
from backend.services.notifier_service import notifier
import logging

router = APIRouter(prefix="/notifications", tags=["Notificações"])


@router.post("/subscribe")
async def subscribe_push(
    subscription: dict,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual)
):
    """Salva ou atualiza o token de push do motorista logado."""
    # get_usuario_atual returns a dict. We must use .get() and link via email
    email = usuario.get("email")
    if not email:
        raise HTTPException(status_code=401, detail="Usuário inválido")

    motorista = db.query(models.Motorista).filter(
        models.Motorista.email == email).first()

    if not motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    # Salvamos o JSON da subscrição no campo 'push_token' do motorista
    motorista.push_token = subscription
    db.commit()

    return {"status": "success"}


@router.delete("/prune-tokens", status_code=status.HTTP_200_OK)
async def prune_invalid_tokens(
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual)
):
    """Remove tokens que não são mais válidos (Otimização de banco)."""
    if usuario.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    # Busca motoristas com tokens
    motoristas = db.query(models.Motorista).filter(
        models.Motorista.push_token.isnot(None)).all()
    removed_count = 0

    for m in motoristas:
        # Tenta um push 'silencioso' de validação
        success = notifier.send_web_push(
            m.push_token, {"title": "ping", "body": "check", "silent": True})
        if not success:
            m.push_token = None
            removed_count += 1

    if removed_count > 0:
        db.commit()

    return {"message": f"Limpeza concluída. {removed_count} tokens inválidos removidos."}


@router.post("/test/{motorista_id}")
async def test_push_notification(
    motorista_id: int,
    db: Session = Depends(get_db),
    usuario=Depends(get_usuario_atual)
):
    """Envia uma notificação de teste para um motorista específico (Apenas Admin)."""
    if usuario.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    motorista = db.query(models.Motorista).filter(
        models.Motorista.id == motorista_id).first()
    if not motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")

    if not motorista.push_token:
        raise HTTPException(
            status_code=400, detail="O motorista ainda não autorizou notificações push no navegador")

    test_data = {
        "title": "🚀 Teste Central Transfers",
        "body": f"Olá {motorista.nome}, este é um teste de push notification do seu PWA!",
        "url": "/",
        "icon": "/icon-192x192.png"
    }

    success = notifier.send_web_push(motorista.push_token, test_data)

    return {"status": "success" if success else "failed", "motorista": motorista.nome}
