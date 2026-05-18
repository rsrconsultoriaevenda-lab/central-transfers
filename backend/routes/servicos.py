from fastapi import APIRouter, Depends, status, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal
from backend.database import get_db
from backend import models, schemas
from backend.auth import get_usuario_atual
from backend.image_service import upload_image_to_cloudinary

router = APIRouter(prefix="/servicos", tags=["Serviços"])


@router.get("/")
def listar_servicos(db: Session = Depends(get_db)):
    return db.query(models.Servico).all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.ServicoResponse)
async def criar_servico(
    nome: str = Form(...),
    tipo: Optional[str] = Form("TRANSFERS"),
    categoria: Optional[str] = Form("TRANSFERS"),
    descricao: str = Form(...),
    capacidade_passageiros: Optional[int] = Form(4),
    capacidade_malas: Optional[int] = Form(2),
    valor: Optional[Decimal] = Form(0.0),
    valor_padrao: Optional[Decimal] = Form(0.0),
    imagem: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    try:
        imagem_url = None
        if imagem:
            imagem_url = await upload_image_to_cloudinary(imagem)

        novo = models.Servico(
            nome=nome,
            tipo=tipo,
            categoria=categoria,
            descricao=descricao,
            capacidade_passageiros=capacidade_passageiros,
            capacidade_malas=capacidade_malas,
            valor=valor,
            valor_padrao=valor_padrao,
            imagem_url=imagem_url
        )
        db.add(novo)
        db.commit()
        db.refresh(novo)
        return novo
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao criar serviço: {str(e)}")
