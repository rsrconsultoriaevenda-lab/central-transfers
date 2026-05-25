import enum
from datetime import datetime, timezone
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    Column,
    Integer,
    String,  # Mantém String
    Float,
    ForeignKey,
    DateTime,
    Boolean,
    Text,
    Numeric,
    JSON,
    Index,
    Enum
)

from sqlalchemy.orm import relationship

from backend.database import Base

# =========================
# ENUMS
# =========================


class StatusPedido(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    ACEITO = "ACEITO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"


# =========================
# SQLALCHEMY MODELS
# =========================

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    # Mantenha consistente com os scripts de setup
    senha_hash = Column(String, nullable=False)
    role = Column(String, default="admin")
    ativo = Column(Boolean, default=True)

    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String, nullable=False)
    telefone = Column(String)
    email = Column(String)

    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))


class Mensalidade(Base):
    __tablename__ = "mensalidades"

    id = Column(Integer, primary_key=True, index=True)
    motorista_id = Column(Integer, ForeignKey("motoristas.id"))
    mes_referencia = Column(String)  # Ex: "2024-05"
    valor = Column(Numeric(10, 2))
    status = Column(String, default="PENDENTE")  # PENDENTE, PAGO
    data_pagamento = Column(DateTime, nullable=True)
    checkout_url = Column(String, nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    motorista = relationship("Motorista", back_populates="mensalidades")


class Motorista(Base):
    __tablename__ = "motoristas"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)

    senha_hash = Column(String, nullable=False)

    carro = Column(String)
    placa = Column(String)
    modelo = Column(String)
    ano = Column(Integer)
    categoria = Column(String, default="STANDARD")
    comissao_master = Column(Numeric(10, 2), default=15.0)

    ativo = Column(Boolean, default=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    ultima_atualizacao = Column(DateTime, nullable=True)
    push_token = Column(JSON, nullable=True)

    status = Column(String, default="ATIVO")

    # TRIAL | MENSAL | EXPIRADO
    plano = Column(String, default="MENSAL")

    mensalidade_ativa = Column(Boolean, default=True)

    vencimento_mensalidade = Column(DateTime, nullable=True)
    data_inicio_trial = Column(
        DateTime, default=lambda: datetime.now(timezone.utc))

    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    mensalidades = relationship("Mensalidade", back_populates="motorista")


class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=True)
    categoria = Column(String, default="TRANSFERS")

    valor = Column(Numeric(10, 2), nullable=False)
    valor_padrao = Column(Numeric(10, 2), default=0.0)

    descricao = Column(Text, nullable=True)
    capacidade_passageiros = Column(Integer, default=4)
    capacidade_malas = Column(Integer, default=2)
    imagem_url = Column(String, nullable=True)

    ativo = Column(Boolean, default=True)


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)

    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    servico_id = Column(Integer, ForeignKey("servicos.id"))
    motorista_id = Column(Integer, ForeignKey("motoristas.id"), nullable=True)

    origem = Column(String, nullable=False)
    destino = Column(String, nullable=False)
    data_servico = Column(DateTime, nullable=False)

    valor = Column(Numeric(10, 2), nullable=False)
    valor_comissao = Column(Numeric(10, 2), default=0.0)
    valor_liquido_motorista = Column(Numeric(10, 2), default=0.0)
    # Comissão padrão da central
    comissao = Column(Numeric(10, 2), default=20.0)
    canal_venda = Column(String, default="direto")
    tipo_comissao_motorista = Column(String, default="AGUARDANDO_ACEITE")

    status = Column(Enum(StatusPedido), default=StatusPedido.PENDENTE)

    observacoes = Column(Text, nullable=True)

    criado_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    cliente = relationship("Cliente")
    motorista = relationship("Motorista")
    servico = relationship("Servico")

    # Índices para busca rápida em produção
    __table_args__ = (
        Index('ix_pedidos_status', 'status'),
        Index('ix_pedidos_data_servico', 'data_servico'),
        Index('ix_pedidos_motorista_id', 'motorista_id'),
    )

    def calcular_financeiro(self):
        """Calcula as comissões com base no plano do motorista."""
        if self.valor is None:
            return

        valor_total = Decimal(str(self.valor))

        if not self.motorista:
            # Se não há motorista, usa a comissão padrão da central definida no pedido
            perc_padrao = Decimal(
                str(self.comissao or "20.0")) / Decimal("100.0")
            self.valor_comissao = (
                valor_total * perc_padrao).quantize(Decimal("0.01"))
            self.tipo_comissao_motorista = "AGUARDANDO_ACEITE"
            self.valor_liquido_motorista = (
                valor_total - self.valor_comissao).quantize(Decimal("0.01"))
            return

        if self.motorista.plano == "MASTER":
            perc = Decimal(
                str(self.motorista.comissao_master or "15.0")) / Decimal("100.0")
            self.valor_comissao = (
                valor_total * perc).quantize(Decimal("0.01"))
            self.tipo_comissao_motorista = "PERCENTUAL_CENTRAL"
        else:
            # Plano Mensal: Motorista fica com 100% do valor do serviço
            self.valor_comissao = Decimal("0.00")
            self.tipo_comissao_motorista = "PLANO_MENSAL"

        self.valor_liquido_motorista = (
            valor_total - self.valor_comissao).quantize(Decimal("0.01"))

    # =========================
    # PYDANTIC SCHEMAS
    # =========================


# Nota: Removidos Schemas Pydantic que estavam duplicados aqui.
# Utilize apenas o arquivo backend/schemas.py para manter a organização.
