from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Numeric
from sqlalchemy.orm import relationship
from backend.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    telefone = Column(String(100), nullable=False)
    email = Column(String(255))

    pedidos = relationship("Pedido", back_populates="cliente")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)


class Motorista(Base):
    __tablename__ = "motoristas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    telefone = Column(String(100), nullable=False)
    carro = Column(String(255), nullable=False)
    placa = Column(String(50), nullable=False)
    modelo = Column(String(255), nullable=False)
    ano = Column(Integer, nullable=False)

    pedidos = relationship("Pedido", back_populates="motorista")


class Servico(Base):
    __tablename__ = "servicos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255), nullable=False)
    tipo = Column(String(255), nullable=False)
    descricao = Column(Text, nullable=False)
    valor_padrao = Column(Numeric(10, 2), default=0.0)

    pedidos = relationship("Pedido", back_populates="servico")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    servico_id = Column(Integer, ForeignKey("servicos.id"), nullable=False)
    motorista_id = Column(Integer, ForeignKey("motoristas.id"), nullable=True)

    origem = Column(String(255), nullable=False)
    destino = Column(String(255), nullable=False)
    data_servico = Column(DateTime, nullable=False)
    valor = Column(Numeric(10, 2), nullable=False)
    observacoes = Column(Text)

    status = Column(String(50), default="PENDENTE")

    cliente = relationship("Cliente", back_populates="pedidos")
    servico = relationship("Servico", back_populates="pedidos")
    motorista = relationship("Motorista", back_populates="pedidos")
