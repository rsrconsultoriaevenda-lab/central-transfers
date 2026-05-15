from pydantic import BaseModel, ConfigDict
from datetime import datetime
from decimal import Decimal
from typing import Optional
from backend.config import settings


class Cliente(BaseModel):
    id: int | None = None
    nome: str
    telefone: str | None = None
    email: str | None = None

    model_config = ConfigDict(from_attributes=True)


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
    ativo: bool = True
    plano: str = "MENSAL"
    comissao_master: Optional[Decimal] = Decimal("10.0")


class Motorista(MotoristaBase):
    id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


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


class MotoristaCreateAdmin(MotoristaBase):
    senha: Optional[str] = None  # Senha é opcional para criação via admin


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
    checkout_url: Optional[str] = None


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
    ativo: bool = True
    id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


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
    valor_comissao: Optional[Decimal] = Decimal("0.0")
    comissao: Optional[Decimal] = Decimal("20.0")
    canal_venda: Optional[str] = "direto"
    observacoes: Optional[str] = None


class PedidoOut(PedidoCreate):
    id: int
    status: str
    valor_liquido_motorista: Optional[Decimal] = Decimal("0.0")
    tipo_comissao_motorista: Optional[str] = "PERCENTUAL_CENTRAL"
    motorista_id: Optional[int] = None
    criado_at: datetime

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class DashboardStats(BaseModel):
    total_pedidos: int
    pendentes: int
    aguardando_pagamento: int
    pagos: int
    aceitos: int
    concluidos: int
    faturamento_total: Decimal


class MotoristaSaldo(BaseModel):
    saldo_total: Decimal
    total_pedidos: int
