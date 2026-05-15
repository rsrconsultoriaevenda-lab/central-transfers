from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend import models, schemas
from backend.database import get_db
from backend.auth import get_usuario_atual

router = APIRouter(prefix="/notifications", tags=["Notificações"])

@router.post("/subscribe")
async def subscribe_push(
    subscription: dict, 
    db: Session = Depends(get_db),
    usuario = Depends(get_usuario_atual)
):
    """Salva ou atualiza o token de push do motorista logado."""
    motorista = db.query(models.Motorista).filter(models.Motorista.id == usuario.id).first()
    if not motorista:
        raise HTTPException(status_code=404, detail="Motorista não encontrado")
    
    # Salvamos o JSON da subscrição no campo 'push_token' do motorista
    motorista.push_token = subscription 
    db.commit()
    
    return {"status": "success"}