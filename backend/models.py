from typing import Optional
from datetime import datetime

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    DateTime,
    Boolean,
    Text,
    Numeric
)

from sqlalchemy.orm import relationship

from pydantic import BaseModel, EmailStr

from backend.database import Base


# =========================
# SQLALCHEMY MODELS
# =========================

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    senha_hash = Column(String, nullable=False)  # Mantenha consistente com os scripts de setup
    role = Column(String, default="admin")
    ativo = Column(Boolean, default=True)

    criado_em = Column(DateTime, default=datetime.utcnow)


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String, nullable=False)
    telefone = Column(String)
    email = Column(String)

    criado_em = Column(DateTime, default=datetime.utcnow)


class Mensalidade(Base):
    __tablename__ = "mensalidades"

    id = Column(Integer, primary_key=True, index=True)
    motorista_id = Column(Integer, ForeignKey("motoristas.id"))
    mes_referencia = Column(String)  # Ex: "2024-05"
    valor = Column(Numeric(10, 2))
    status = Column(String, default="PENDENTE")  # PENDENTE, PAGO
    data_pagamento = Column(DateTime, nullable=True)
    checkout_url = Column(String, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow)

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

    status = Column(String, default="ATIVO")

    # TRIAL | MENSAL | EXPIRADO
    plano = Column(String, default="MENSAL")

    mensalidade_ativa = Column(Boolean, default=True)

    vencimento_mensalidade = Column(DateTime, nullable=True)
    data_inicio_trial = Column(DateTime, default=datetime.utcnow)

    criado_em = Column(DateTime, default=datetime.utcnow)

    mensalidades = relationship("Mensalidade", back_populates="motorista")


class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String, nullable=False)
    tipo = Column(String, nullable=True)

    valor = Column(Numeric(10, 2), nullable=False)

    descricao = Column(Text, nullable=True)

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

    status = Column(String, default="PENDENTE")

    observacoes = Column(Text, nullable=True)

    criado_at = Column(DateTime, default=datetime.utcnow)

    cliente = relationship("Cliente")
    motorista = relationship("Motorista")
    servico = relationship("Servico")

    def calcular_financeiro(self):
        """Calcula as comissões com base no plano do motorista."""
        from decimal import Decimal
        if self.valor is None:
            return

        valor_total = Decimal(str(self.valor))

        if not self.motorista:
            # Se não há motorista, usa a comissão padrão de 20%
            self.valor_comissao = (valor_total * Decimal("0.20")).quantize(Decimal("0.01"))
            self.valor_liquido_motorista = (valor_total - self.valor_comissao).quantize(Decimal("0.01"))
            return

        if self.motorista.plano == "MASTER":
            perc = Decimal(str(self.motorista.comissao_master or "15.0")) / Decimal("100.0")
            self.valor_comissao = (valor_total * perc).quantize(Decimal("0.01"))
            self.tipo_comissao_motorista = "PERCENTUAL_CENTRAL"
        else:
            # Plano Mensal: Motorista fica com 100% do valor do serviço
            self.valor_comissao = Decimal("0.00")
            self.tipo_comissao_motorista = "PLANO_MENSAL"

        self.valor_liquido_motorista = (valor_total - self.valor_comissao).quantize(Decimal("0.01"))

    # =========================
    # PYDANTIC SCHEMAS
    # =========================


# Nota: Removidos Schemas Pydantic que estavam duplicados aqui. 
# Utilize apenas o arquivo backend/schemas.py para manter a organização.
