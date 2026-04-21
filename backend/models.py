from sqlalchemy import Column, Integer, String
from database import Base

class Motorista(Base):
    __tablename__ = "motoristas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String)
    telefone = Column(String)
    carro = Column(String)