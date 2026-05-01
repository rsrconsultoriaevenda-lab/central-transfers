from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text, Boolean, func
from sqlalchemy.orm import relationship
from backend.database import Base
import datetime


class Motorista(Base):
    __tablename__ = "motoristas"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255))
    telefone = Column(String(50))
    carro = Column(String(255))
    placa = Column(String(50))
    modelo = Column(String(255))
    ano = Column(Integer)
    status = Column(String(50), default="ATIVO")
    plano = Column(String(50), default="MENSAL")  # MENSAL ou MASTER
    ativo = Column(Boolean, default=True)
    pedidos = relationship("Pedido", back_populates="motorista")


class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255))
    telefone = Column(String(50))
    email = Column(String(255))
    pedidos = relationship("Pedido", back_populates="cliente")


class Servico(Base):
    __tablename__ = "servicos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255))
    tipo = Column(String(100))
    descricao = Column(Text, nullable=True)
    valor_padrao = Column(Numeric(10, 2), default=0.0)
    ativo = Column(Boolean, default=True)
    pedidos = relationship("Pedido", back_populates="servico")


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    senha = Column(String(255))
    role = Column(String(50), default="cliente")  # Adicionado campo role
    # No direct relationship to Pedido here, as Pedido is linked to Cliente


class Pedido(Base):
    __tablename__ = "pedidos"
    id = Column(Integer, primary_key=True, index=True)
    origem = Column(String(255))
    destino = Column(String(255))
    data_servico = Column(DateTime, default=datetime.datetime.utcnow)
    criado_at = Column(DateTime, server_default=func.now())
    valor = Column(Numeric(10, 2))
    valor_comissao = Column(Numeric(10, 2), default=0.0)
    observacoes = Column(Text, nullable=True)
    status = Column(String(50), default="PENDENTE")
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    servico_id = Column(Integer, ForeignKey("servicos.id"))
    motorista_id = Column(Integer, ForeignKey("motoristas.id"), nullable=True)

    cliente = relationship("Cliente", back_populates="pedidos")
    servico = relationship("Servico", back_populates="pedidos")
    motorista = relationship("Motorista", back_populates="pedidos")
