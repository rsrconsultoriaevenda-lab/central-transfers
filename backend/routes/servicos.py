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
@router.get("")
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


@router.put("/{servico_id}/")
@router.put("/{servico_id}", response_model=schemas.ServicoResponse)
async def atualizar_servico(
    servico_id: int,
    nome: Optional[str] = Form(None),
    tipo: Optional[str] = Form(None),
    categoria: Optional[str] = Form(None),
    descricao: Optional[str] = Form(None),
    capacidade_passageiros: Optional[int] = Form(None),
    capacidade_malas: Optional[int] = Form(None),
    valor: Optional[Decimal] = Form(None),
    valor_padrao: Optional[Decimal] = Form(None),
    imagem: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    user: dict = Depends(get_usuario_atual)
):
    if user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Acesso negado")

    servico = db.query(models.Servico).filter(
        models.Servico.id == servico_id).first()
    if not servico:
        raise HTTPException(status_code=404, detail="Serviço não encontrado")

    try:
        if imagem:
            servico.imagem_url = await upload_image_to_cloudinary(imagem)

        # Atualização parcial (apenas campos enviados)
        if nome is not None:
            servico.nome = nome
        if tipo is not None:
            servico.tipo = tipo
        if categoria is not None:
            servico.categoria = categoria
        if descricao is not None:
            servico.descricao = descricao
        if capacidade_passageiros is not None:
            servico.capacidade_passageiros = capacidade_passageiros
        if capacidade_malas is not None:
            servico.capacidade_malas = capacidade_malas
        if valor is not None:
            servico.valor = valor
        if valor_padrao is not None:
            servico.valor_padrao = valor_padrao

        db.commit()
        db.refresh(servico)
        return servico
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Erro ao atualizar serviço: {str(e)}")
