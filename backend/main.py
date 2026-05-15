from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

# 1. Imports de configuração e serviços
from backend.config import settings
from backend.services.notifier_service import ConnectionManager
from backend.routes import pagamentos, whatsapp, auth, health
from backend.setup_admin import criar_admin_mestre

logger = logging.getLogger(__name__)

# 2. Definição do Ciclo de Vida (Lifespan)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Iniciando aplicação Central Transfers...")
    try:
        criar_admin_mestre()
    except Exception as e:
        logger.error(f"Erro ao inicializar Admin Mestre: {e}")

        app.state.notifier = ConnectionManager()
        logger.info("Aplicação iniciada e serviços essenciais carregados.")
        yield
        logger.info("Encerrando aplicação Central Transfers...")

        # --- CHECKPOINT CRÍTICO: O 'app' DEVE ser definido aqui ---
        app = FastAPI(lifespan=lifespan)

        # 3. Middlewares
        app.add_middleware(
            CORSMiddleware,
            allow_origins=settings.get_allowed_origins(),
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 4. Inclusão de Rotas
        app.include_router(health.router)
        app.include_router(pagamentos.router)
        app.include_router(whatsapp.router)
        app.include_router(auth.router)

        # 5. Endpoints (Websocket e Raiz)


@app.websocket("/ws/{motorista_id}")
async def websocket_endpoint(websocket: WebSocket, motorista_id: int):
    manager: ConnectionManager = app.state.notifier
    await manager.connect(websocket, motorista_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(motorista_id)
    except Exception as e:
        logger.error(
            f"Erro na conexão WebSocket para motorista {motorista_id}: {e}")
        manager.disconnect(motorista_id)


@app.get("/test-broadcast")
async def test_broadcast():
    manager: ConnectionManager = app.state.notifier
    await manager.notify_drivers({
        "type": "TEST_NOTIFICATION",
        "mensagem": "🚨 TESTE: Novo pedido disponível!",
        "valor": "250.00"
    })
    return {"status": "Notificação enviada com sucesso"}


@app.get("/")
async def root():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "environment": settings.ENV,
        "database": "connected",
        "docs": "/docs"
    }
from fastapi import WebSocket, WebSocketException, status, Query, Depends
from typing import Annotated

# Supondo que você tenha uma função de validação no seu módulo backend/auth/
# from backend.auth.service import decode_access_token 

async def get_token_auth(
    websocket: WebSocket,
    token: Annotated[str | None, Query()] = None,
):
    """
    Dependência para validar o token JWT via Query Parameter.
    Se o token for inválido ou ausente, fecha a conexão.
    """
    if token is None:
        # WS_1008_POLICY_VIOLATION é o código padrão para falha de política/auth
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    
    # Exemplo de lógica de validação:
    # user = decode_access_token(token)
    # if not user:
    #     raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION)
    
    return token # Ou retorne o objeto do usuário/motorista decodificado

@app.websocket("/ws/{motorista_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    motorista_id: int,
    token: Annotated[str, Depends(get_token_auth)] # A autenticação acontece aqui
):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            # Lógica de processamento...
    except Exception:
        # Tratar desconexões
        pass
