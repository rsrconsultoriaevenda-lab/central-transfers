from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from typing import Optional


class ClienteBase(BaseModel):
    nome: str
    telefone: str
    email: Optional[str] = None


class Cliente(ClienteBase):
    id: Optional[int] = None
    empresa_id: Optional[int] = None

    class Config:
        from_attributes = True


class MotoristaBase(BaseModel):
    nome: str
    telefone: str
    carro: str
    placa: str
    modelo: str
    ano: int
    # Adicionado para consistência com o frontend
    categoria: Optional[str] = "STANDARD"
    data_inicio_trial: Optional[datetime] = None # Novo campo
    status: str = "ATIVO"
    plano: str = "MENSAL"
    empresa_id: Optional[int] = None


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
    # Pode ser fornecido se o app for white-label ou selecionado
    empresa_id: Optional[int] = None


class MotoristaStatusUpdate(BaseModel):
    status: str  # Ex: "ATIVO", "PENDENTE_APROVACAO", "REJEITADO"


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
    empresa_id: Optional[int] = None
    id: Optional[int] = None

    class Config:
        from_attributes = True


class PedidoCreate(BaseModel):
    cliente_id: int
    servico_id: int
    origem: str
    destino: str
    data_servico: datetime
    valor: Decimal
    valor_comissao: Optional[Decimal] = 0.0
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
    email: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    senha: str


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


class CorridaCreate(BaseModel):
    origem: str
    destino: str
    data: Optional[datetime] = None


class CorridaOut(BaseModel):
    id: int
    origem: str
    destino: str
    data: datetime
    status: str
    usuario_id: int
    motorista_id: Optional[int] = None

    class Config:
        from_attributes = True
