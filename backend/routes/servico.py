from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ServicoCreate(BaseModel):
    tipo: str
    origem: str
    destino: str
    descricao: Optional[str] = None
    data_hora: Optional[datetime] = None


class ServicoUpdateStatus(BaseModel):
    status: str


class ServicoResponse(BaseModel):
    id: int
    tipo: str
    origem: str
    destino: str
    descricao: Optional[str]
    status: str

    class Config:
        from_attributes = True