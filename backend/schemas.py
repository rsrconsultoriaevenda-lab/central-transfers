from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional


class ClienteBase(BaseModel):
    nome: str
    telefone: str
    email: Optional[str] = None


class Cliente(ClienteBase):
    id: Optional[int]
    class Config:
        from_attributes = True


class MotoristaBase(BaseModel):
    nome: str
    telefone: str
    carro: str
    placa: str
    modelo: str
    ano: int


class Motorista(MotoristaBase):
    id: Optional[int]
    class Config:
        from_attributes = True


class Servico(BaseModel):
    nome: str
    tipo: str   
    descricao: str
    id: Optional[int]
    class Config:
        from_attributes = True


class PedidoCreate(BaseModel):
    cliente_id: int
    servico_id: int
    origem: str
    destino: str
    data_servico: datetime
    valor: Decimal
    observacoes: Optional[str] = None


class PedidoOut(PedidoCreate):
    id: int
    status: str
    class Config:
        from_attributes = True


class AtribuirMotorista(BaseModel):
    motorista_id: int


class PedidoStatusUpdate(BaseModel):
    status: str


class WhatsAppIncoming(BaseModel):
    sender: str
    message: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UsuarioCreate(BaseModel):
    username: str
    password: str

class DashboardStats(BaseModel):
    total_pedidos: int
    pendentes: int
    aguardando_pagamento: int
    pagos: int
    aceitos: int
    concluidos: int
    faturamento_total: Decimal