import React, { useEffect } from 'react';
import axios from 'axios';

const PWAIntegration: React.FC = () => {
  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';
  const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY;

  useEffect(() => {
    const registerAndSubscribe = async () => {
      if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
        console.warn('Push não suportado neste navegador.');
        return;
      }

      try {
        // 1. Registro do SW
        const registration = await navigator.serviceWorker.register('/sw.js');
        console.log('✅ Service Worker registrado');

        // 2. Solicitação de Permissão Contextual
        if (Notification.permission === 'default') {
          const permission = await Notification.requestPermission();
          if (permission !== 'granted') return;
        }

        // 3. Subscrição Push
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY)
        });

        // 4. Envio para o Backend
        const token = localStorage.getItem('token');
        if (token) {
          await axios.post(`${API_URL}/motoristas/push-token`, subscription, {
            headers: { Authorization: `Bearer ${token}` }
          });
          console.log('🚀 Token de Push sincronizado com o servidor');
        }

      } catch (error) {
        console.error('❌ Erro na integração PWA:', error);
      }
    };

    registerAndSubscribe();
  }, [API_URL, VAPID_PUBLIC_KEY]);

  return null; // Componente lógico, não renderiza UI
};

// Função auxiliar para converter a chave VAPID
function urlBase64ToUint8Array(base64String: string) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

export default PWAIntegration;# backend/models.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

# Assumindo que Base é definida em database.py e importada aqui
# Ex: Base = declarative_base()
# Se você já tem 'Base' importada de 'backend.database', mantenha a importação existente.
from backend.database import Base # Ajuste conforme sua importação real de Base

class StatusPedido(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    ACEITO = "ACEITO"
    CONCLUIDO = "CONCLUIDO"
    CANCELADO = "CANCELADO"

class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"))
    servico_id = Column(Integer, ForeignKey("servicos.id"))
    motorista_id = Column(Integer, ForeignKey("motoristas.id"), nullable=True)
    origem = Column(String, index=True)
    destino = Column(String)
    data_servico = Column(DateTime)
    valor = Column(Float)
    valor_comissao = Column(Float, default=0.0)
    status = Column(Enum(StatusPedido), default=StatusPedido.PENDENTE)
    observacoes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    cliente = relationship("Cliente", back_populates="pedidos")
    servico = relationship("Servico", back_populates="pedidos")
    motorista = relationship("Motorista", back_populates="pedidos")

    # Adicionando índices para busca rápida
    __table_args__ = (
        Index('ix_pedidos_status', 'status'),
        Index('ix_pedidos_data_servico', 'data_servico'),
        Index('ix_pedidos_motorista_id', 'motorista_id'),
    )

# ... (outras classes de modelo como Usuario, Motorista, Cliente, Servico, Mensalidade)
