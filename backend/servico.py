from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ServicoBase(BaseModel):
    nome: str
    tipo: str
    categoria: Optional[str] = "TRANSFERS"
    descricao: Optional[str] = None
    valor: Optional[float] = 0.0
    imagem_url: Optional[str] = None
    ativo: Optional[bool] = True


class ServicoCreate(ServicoBase):
    pass


class ServicoUpdateStatus(BaseModel):
    status: str


class ServicoResponse(ServicoBase):
    id: int

    class Config:
        from_attributes = True
