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
    data_inicio_trial = Column(DateTime, nullable=True) # Novo campo para o período de teste
    plano = Column(String(50), default="MENSAL")  # MENSAL ou MASTER
    ativo = Column(Boolean, default=True)
    empresa_id = Column(Integer, ForeignKey("usuarios.id"),
                        index=True)  # ID do Admin/Dono
    pedidos = relationship("Pedido", back_populates="motorista")


class Mensalidade(Base):
    __tablename__ = "mensalidades"
    id = Column(Integer, primary_key=True, index=True)
    motorista_id = Column(Integer, ForeignKey("motoristas.id"))
    mes_referencia = Column(String(7))  # Formato "YYYY-MM"
    valor = Column(Numeric(10, 2))
    data_vencimento = Column(DateTime)
    data_pagamento = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDENTE")  # PENDENTE, PAGO, ATRASADO
    empresa_id = Column(Integer, ForeignKey("usuarios.id"), index=True)


class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255))
    telefone = Column(String(50))
    email = Column(String(255))
    empresa_id = Column(Integer, ForeignKey("usuarios.id"), index=True)
    pedidos = relationship("Pedido", back_populates="cliente")


class Servico(Base):
    __tablename__ = "servicos"
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255))
    tipo = Column(String(100))
    categoria = Column(String(100), default="TRANSFERS")
    descricao = Column(Text, nullable=True)
    capacidade_passageiros = Column(Integer, default=4)
    capacidade_malas = Column(Integer, default=2)
    valor = Column(Numeric(10, 2), default=0.0)
    valor_padrao = Column(Numeric(10, 2), default=0.0)
    imagem_url = Column(String(500), nullable=True)
    ativo = Column(Boolean, default=True)
    empresa_id = Column(Integer, ForeignKey("usuarios.id"), index=True)
    pedidos = relationship("Pedido", back_populates="servico")


class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    senha = Column(String(255))
    # Se for nulo, ele é o dono da empresa
    empresa_id = Column(Integer, nullable=True)
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
    # Valor que o motorista recebe
    valor_liquido_motorista = Column(Numeric(10, 2), default=0.0)
    # Ex: PERCENTUAL_CENTRAL, MENSALIDADE_FIXA
    tipo_comissao_motorista = Column(String(50), default="PERCENTUAL_CENTRAL")
    # ex: google, instagram, whatsapp
    canal_venda = Column(String(100), default="direto")
    # Percentual da comissão (ex: 20%)
    comissao = Column(Numeric(10, 2), default=20.0)
    observacoes = Column(Text, nullable=True)
    status = Column(String(50), default="PENDENTE")
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    servico_id = Column(Integer, ForeignKey("servicos.id"))
    motorista_id = Column(Integer, ForeignKey("motoristas.id"), nullable=True)
    empresa_id = Column(Integer, ForeignKey("usuarios.id"), index=True)

    cliente = relationship("Cliente", back_populates="pedidos")
    servico = relationship("Servico", back_populates="pedidos")
    motorista = relationship("Motorista", back_populates="pedidos")
