import logging
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware

# Importação dos roteadores operacionais do ecossistema Central Transfers
from backend.routes import (
    auth,
    pedidos,
    clientes,
    motoristas,
    servicos,
    dashboard,
    pagamentos,
    whatsapp,
    health
)

# Configuração de Logs para auditoria local e em produção (Railway)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CentralTransfers")

# Inicialização limpa do FastAPI com suporte nativo a redirecionamento seguro de trailing slash
app = FastAPI(
    title="Central Transfers API",
    description="Backend de logística para gestão de transfers Aeroporto POA / Gramado",
    version="1.0.0"
)

# ======================================================================
# CONFIGURAÇÃO DE CORS EXPANDIDA PARA PRODUÇÃO (VERCEL & RAILWAY)
# ======================================================================
# Declaramos explicitamente as origens permitidas (Local, Vercel e subdomínios)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://central-transfers.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# ======================================================================
# MIDDLEWARE INTERCEPTADOR PARA PREFLIGHT (OPTIONS) - BLINDAGEM CORS
# ======================================================================
@app.middleware("http")
async def interceptar_cors_preflight(request: Request, call_next):
    # Se o navegador mandar um OPTIONS (Preflight), respondemos imediatamente com os headers de sucesso
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        origin = request.headers.get("Origin")
        if origin in origins or "*" in origins:
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, X-Requested-With"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

        return await call_next(request)

        # ======================================================================
        # MAPEAMENTO DE ROTAS COM DUPLO PREFIXO (ESTRATÉGIA ANTI-CACHE DO FRONT)
        # ======================================================================

        # 1️⃣ Mapeamento Direto (Caso o frontend chame /motoristas, /pedidos, etc.)
        app.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
        app.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos & Corridas"])
        app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
        app.include_router(motoristas.router, prefix="/motoristas", tags=["Motoristas"])
        app.include_router(servicos.router, prefix="/servicos", tags=["Serviços de Transfer"])
        app.include_router(dashboard.router, prefix="/dashboard", tags=["Painel Administrativo"])
        app.include_router(pagamentos.router, prefix="/pagamentos", tags=["Mercado Pago & Finanças"])
        app.include_router(whatsapp.router, prefix="/whatsapp", tags=["Notificações WhatsApp"])
        app.include_router(health.router, prefix="/health", tags=["Saúde do Sistema"])

        # 2️⃣ Mapeamento Espelhado com /api (Caso o frontend tente forçar /api/motoristas, etc.)
        app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
        app.include_router(pedidos.router, prefix="/api/pedidos", tags=["Pedidos & Corridas"])
        app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
        app.include_router(motoristas.router, prefix="/api/motoristas", tags=["Motoristas"])
        app.include_router(servicos.router, prefix="/api/servicos", tags=["Serviços de Transfer"])
        app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Painel Administrativo"])
        app.include_router(pagamentos.router, prefix="/api/pagamentos", tags=["Mercado Pago & Finanças"])
        app.include_router(whatsapp.router, prefix="/api/whatsapp", tags=["Notificações WhatsApp"])
        app.include_router(health.router, prefix="/api/health", tags=["Saúde do Sistema"])

        # ======================================================================
        # ROTA DE LOGÍSTICA EM TEMPO REAL (WEBSOCKETS DE ISOLAMENTO)
        # ======================================================================
@app.websocket("/ws/teste_limpo/{driver_id}")
@app.websocket("/api/ws/teste_limpo/{driver_id}")
async def teste_limpo(websocket: WebSocket, driver_id: int):
    await websocket.accept()
    logger.info(f"🟢 [TESTE LIMPO] Motorista {driver_id} conectou com sucesso na malha de rede!")
    try:
        await websocket.send_json({"type": "SISTEMA", "mensagem": "Conexão direta bem-sucedida!"})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        logger.info(f"🔴 [TESTE LIMPO] Motorista {driver_id} encerrou a sessão remota.")

        # ======================================================================
        # EVENTOS DO CICLO DE VIDA DO SERVIDOR (STARTUP / SHUTDOWN)
        # ======================================================================
@app.on_event("startup")
async def startup_event():
    logger.info("🚀 Central Transfers inicializado com sucesso!")
    logger.info("🔒 Filtros de CORS aplicados. Middleware de Preflight e Roteamento duplo ativos.")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("🛑 Encerrando conexões e desligando Central Transfers com segurança...")
    
    
