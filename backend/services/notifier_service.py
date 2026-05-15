from fastapi import WebSocket
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Gerencia conexões WebSocket para notificações em tempo real (estilo Uber)."""

    def __init__(self):
        # Armazena conexões ativas: { motorista_id: websocket }
        self.active_connections: Dict[int, WebSocket] = {}

    async def connect(self, websocket: WebSocket, motorista_id: int):
        await websocket.accept()
        self.active_connections[motorista_id] = websocket
        logger.info(f"Motorista {motorista_id} conectado ao WebSocket.")

    def disconnect(self, motorista_id: int):
        if motorista_id in self.active_connections:
            del self.active_connections[motorista_id]
            logger.info(f"Motorista {motorista_id} desconectado.")

    async def notify_drivers(self, message: dict):
        """Envia uma mensagem para todos os motoristas online."""
        disconnected = []
        for mid, ws in self.active_connections.items():
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(mid)

        for mid in disconnected:
            self.disconnect(mid)
