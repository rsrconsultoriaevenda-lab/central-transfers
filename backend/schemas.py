from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional


class Cliente(BaseModel):
    id: int | None = None
    nome: str
    telefone: str | None = None
    email: str | None = None

    class Config:
        from_attributes = True


class MotoristaBase(BaseModel):
    nome: str
    telefone: str
    carro: str
    placa: str
    modelo: str
    ano: int
    categoria: Optional[str] = "STANDARD"
    data_inicio_trial: Optional[datetime] = None
    status: str = "ATIVO"
    plano: str = "MENSAL"


class Motorista(MotoristaBase):
    id: Optional[int] = None

    class Config:
        from_attributes = True


class MotoristaAcesso(BaseModel):
    login: str
    senha: Optional[str] = None


class MotoristaCreateResponse(BaseModel):
    motorista: Motorista
    acesso: MotoristaAcesso


class MotoristaRegister(BaseModel):
    nome: str
    telefone: str
    carro: str
    placa: str
    modelo: str
    ano: int
    senha: str
    categoria: Optional[str] = "STANDARD"


class MotoristaStatusUpdate(BaseModel):
    status: str


class MensalidadeBase(BaseModel):
    motorista_id: int
    mes_referencia: str
    valor: Decimal
    status: str = "PENDENTE"


class MensalidadeOut(MensalidadeBase):
    id: int
    data_pagamento: Optional[datetime] = None


class Servico(BaseModel):
    nome: str
    tipo: Optional[str] = "TRANSFERS"
    categoria: Optional[str] = "TRANSFERS"
    descricao: str
    capacidade_passageiros: Optional[int] = 4
    capacidade_malas: Optional[int] = 2
    valor: Optional[Decimal] = 0.0
    valor_padrao: Optional[Decimal] = 0.0
    imagem_url: Optional[str] = None
    id: Optional[int] = None

    class Config:
        from_attributes = True


class ServicoUpdateStatus(BaseModel):
    status: str


class ServicoResponse(Servico):
    id: int


class PedidoCreate(BaseModel):
    cliente_id: int
    servico_id: int
    origem: str
    destino: str
    data_servico: datetime
    valor: Decimal
    valor_comissao: Optional[Decimal] = 0.0
    comissao: Optional[Decimal] = 20.0
    canal_venda: Optional[str] = "direto"
    observacoes: Optional[str] = None


class PedidoOut(PedidoCreate):
    id: int
    status: str

    class Config:
        from_attributes = True


class PedidoStatusUpdate(BaseModel):
    status: str


class AtribuirMotorista(BaseModel):
    motorista_id: int


class WhatsAppIncoming(BaseModel):
    sender: str
    message: str


class LoginRequest(BaseModel):
    email: str
    senha: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class UsuarioCreate(BaseModel):
    email: str
    senha: str


class UsuarioResponse(BaseModel):
    id: int
    email: str
    role: str

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    total_pedidos: int
    pendentes: int
    aguardando_pagamento: int
    pagos: int
    aceitos: int
    concluidos: int
    faturamento_total: Decimal
