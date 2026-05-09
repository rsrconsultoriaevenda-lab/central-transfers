from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric, Text, Boolean, func
from decimal import Decimal
from sqlalchemy.orm import relationship
from backend.database import Base


class Motorista(Base):
    __tablename__ = "motoristas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(255))
    telefone = Column(String(50))
    carro = Column(String(255))
    placa = Column(String(50))
    modelo = Column(String(255))
    ano = Column(Integer)
    categoria = Column(String(50), default="STANDARD")
    status = Column(String(50), default="ATIVO")

    # Novo campo para o período de teste
    data_inicio_trial = Column(DateTime, nullable=True)

    # MENSAL ou MASTER
    ativo = Column(Boolean, default=True)
    plano = Column(String(50), default="MENSAL")
    comissao_master = Column(Numeric(10, 2), default=10.0) # 5% a 15%

    pedidos = relationship("Pedido", back_populates="motorista")


class Mensalidade(Base):
    __tablename__ = "mensalidades"

    id = Column(Integer, primary_key=True, index=True)
    motorista_id = Column(Integer, ForeignKey("motoristas.id"))
    mes_referencia = Column(String(7))  # Formato "YYYY-MM"
    valor = Column(Numeric(10, 2))
    data_vencimento = Column(DateTime)

    # PENDENTE, PAGO, ATRASADO
    data_pagamento = Column(DateTime, nullable=True)
    status = Column(String(50), default="PENDENTE")
    checkout_url = Column(String(500), nullable=True)


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
    categoria = Column(String(100), default="TRANSFERS")
    descricao = Column(Text, nullable=True)
    capacidade_passageiros = Column(Integer, default=4)
    capacidade_malas = Column(Integer, default=2)
    valor = Column(Numeric(10, 2), default=0.0)
    valor_padrao = Column(Numeric(10, 2), default=0.0)

    imagem_url = Column(String(500), nullable=True)
    ativo = Column(Boolean, default=True)

    pedidos = relationship("Pedido", back_populates="servico")


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True)
    senha = Column(String(255))
    role = Column(String(50), default="cliente")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    origem = Column(String(255))
    destino = Column(String(255))

    data_servico = Column(DateTime, default=func.now())
    criado_at = Column(DateTime, server_default=func.now())

    valor = Column(Numeric(10, 2))
    valor_comissao = Column(Numeric(10, 2), default=0.0)
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

    cliente = relationship("Cliente", back_populates="pedidos")
    servico = relationship("Servico", back_populates="pedidos")
    motorista = relationship("Motorista", back_populates="pedidos")

    def calcular_financeiro(self):
        """
        Calcula automaticamente a comissão da central e o valor líquido do motorista.
        Motorista só recebe por serviços de transporte (categoria TRANSFERS).
        """
        valor_total = self.valor if self.valor else Decimal("0.0")
        
        # Regra: Plataforma retém 100% de serviços que não sejam transporte
        is_transporte = self.servico and self.servico.categoria == "TRANSFERS"
        
        if not is_transporte:
            self.valor_comissao = valor_total
            self.valor_liquido_motorista = Decimal("0.0")
            self.tipo_comissao_motorista = "PLATAFORMA_FULL"
            return

        if self.motorista:
            if self.motorista.plano == 'MASTER':
                # Plano Master: Comissão variável (5-15%)
                percentual = self.motorista.comissao_master if self.motorista.comissao_master else Decimal("10.0")
                self.valor_comissao = valor_total * (percentual / Decimal("100.0"))
                self.valor_liquido_motorista = valor_total - self.valor_comissao
                self.tipo_comissao_motorista = "PERCENTUAL_CENTRAL"
            else:
                # No plano MENSAL (Standard), o motorista recebe o valor integral do transporte
                self.valor_comissao = Decimal("0.0")
                self.valor_liquido_motorista = valor_total 
                self.tipo_comissao_motorista = "STANDARD_ASSINATURA"
        else:
            self.valor_liquido_motorista = Decimal("0.0")
