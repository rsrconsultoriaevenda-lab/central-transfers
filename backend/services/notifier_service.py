import logging
from typing import Dict
from fastapi import WebSocket

logger = logging.getLogger("CentralTransfers")


class NotifierService:
    def __init__(self):
        # Mapeia o ID do motorista para a sua respectiva conexão WebSocket ativa
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, motorista_id: int):
        """Aceita a conexão do motorista e o adiciona ao pool ativo."""
        await websocket.accept()
        self.active_connections[motorista_id] = websocket
        logger.info(
            f"🔌 [Notifier] Motorista {motorista_id} registrado no pool de notificações.")

    def disconnect(self, motorista_id: int):
        """Remove o motorista do pool de conexões ativas."""
        if motorista_id in self.active_connections:
            del self.active_connections[motorista_id]
            logger.info(
                f"❌ [Notifier] Motorista {motorista_id} removido do pool.")

    async def broadcast(self, message: dict):
        """Envia uma mensagem JSON para todos os motoristas conectados simultaneamente."""
        disconnected = []

        # 1. Criamos uma cópia das chaves para iterar com segurança sem erro de mutação
        motoristas_ids = list(self.active_connections.keys())

        for m_id in motoristas_ids:
            connection = self.active_connections.get(m_id)
            if not connection:
                continue
            try:
                # Envia o pacote JSON (garante o envio de 'type' e 'mensagem')
                await connection.send_json(message)
            except Exception as e:
                logger.warning(
                    f"⚠️ Falha ao enviar broadcast para motorista {m_id}: {e}")
                disconnected.append(m_id)

        # 2. Desconecta os motoristas fantasmas FORA do loop principal
        for m_id in disconnected:
            self.disconnect(m_id)


# Instância global do serviço para ser importada nos roteadores (pedidos, pagamentos, etc.)
notifier = NotifierService()
