import sys
import requests

# 1. DEFINIÇÃO DA URL BASE
url = "https://central-transfers-production.up.railway.app"
health_url = f"{url}/health"
webhook_url = f"{url}/pagamentos/webhook"

print("\n--- 1. Iniciando Validação do Ambiente de Produção ---")
print(f"[INFO] Testando rota principal: {health_url}")

try:
    resp = requests.get(health_url, timeout=10)
    if resp.status_code == 200:
        print(f"[OK] Status Geral: Sistema pronto para uso (HTTP 200).")
    else:
        print(
            f"❌ [ERRO] API ({health_url}) retornou status {resp.status_code}")
except requests.exceptions.RequestException as e:
    print(f"❌ [ERRO] Não foi possível conectar à API principal: {e}")

print("\n--- 2. Verificando Webhook Mercado Pago ---")
print(f"[INFO] Testando endpoint: {webhook_url}")

payload_teste = {
    "action": "payment.updated",
    "type": "payment",
    "data": {"id": "123456"}
}

try:
    resp_web = requests.post(webhook_url, json=payload_teste, timeout=10)
    if resp_web.status_code == 200:
        print(f"[OK] Webhook MP respondendo corretamente: HTTP 200")
    elif resp_web.status_code == 403:
        print(f"[OK] Rota existe, mas acesso negado (Esperado sem HMAC válido).")
    else:
        print(f"[INFO] Resposta do Webhook: HTTP {resp_web.status_code}")
except requests.exceptions.RequestException as e:
    print(f"⚠️ [AVISO] Webhook não respondeu: {e}")

print("\n--- Validação Concluída ---")
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.services.notifier_service import notifier

# Importação dos roteadores operacionais do ecossistema Central Transfers
from backend.routes import (
    auth,
    pedidos,
    clientes,
    motoristas,
    servicos,
    dashboard,
    pagamentos,
    notifications,
    health
)

# Configuração de Logs para auditoria local e em produção (Railway)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CentralTransfers")

# Configuração opcional de Sentry para Produção
SENTRY_DSN = getattr(settings, "SENTRY_DSN", None)
if SENTRY_DSN and settings.ENV == "production":
    try:
        import sentry_sdk
        sentry_sdk.init(dsn=SENTRY_DSN, traces_sample_rate=1.0)
        logger.info("🛡️ Monitoramento Sentry ativado.")
    except ImportError:
        logger.warning("⚠️ Sentry SDK não instalado.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Eventos de Inicialização (Startup)
    logger.info("🚀 Central Transfers inicializado com sucesso!")
    logger.info(
        "🔒 Filtros de CORS aplicados. Middleware de Preflight e Roteamento duplo ativos.")
    yield
    # Eventos de Encerramento (Shutdown)
    logger.info(
        "🛑 Encerrando conexões e desligando Central Transfers com segurança...")

app = FastAPI(
    title="Central Transfers API",
    description="Backend de logística para gestão de transfers Aeroporto POA / Gramado",
    version="1.0.0",
    lifespan=lifespan
)

# Expondo o serviço global de notificações ao estado da aplicação
app.state.notifier = notifier

# ======================================================================
# CONFIGURAÇÃO DE CORS EXPANDIDA PARA PRODUÇÃO (VERCEL & RAILWAY)
# ======================================================================
raw_origins = getattr(settings, "ALLOWED_ORIGINS", "")
if raw_origins and raw_origins.strip() == "*":
    origins = ["*"]
else:
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()] if raw_origins else []

    if not origins:
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


@app.middleware("http")
async def interceptar_cors_preflight(request: Request, call_next):
    if request.method == "OPTIONS":
        response = Response(status_code=200)
        origin = request.headers.get("Origin")
        response.headers["Access-Control-Allow-Origin"] = origin or "*"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type, Accept, Origin, X-Requested-With"
        response.headers["Access-Control-Allow-Credentials"] = "true"
        return response
    return await call_next(request)

# ======================================================================
# MAPEAMENTO DE ROTAS COM DUPLO PREFIXO
# ======================================================================

# 1️⃣ Mapeamento Direto
app.include_router(auth.router, tags=["Autenticação"])
app.include_router(pedidos.router, tags=["Pedidos & Corridas"])
app.include_router(clientes.router, tags=["Clientes"])
app.include_router(motoristas.router, prefix="/motoristas",
                   tags=["Motoristas"])
app.include_router(servicos.router, tags=["Serviços de Transfer"])
app.include_router(dashboard.router, tags=["Painel Administrativo"])
app.include_router(notifications.router, tags=["Notificações"])
app.include_router(health.router, tags=["Saúde do Sistema"])
app.include_router(pagamentos.router, prefix="/pagamentos",
                   tags=["Mercado Pago & Finanças"])

# 2️⃣ Mapeamento Espelhado com /api
app.include_router(auth.router, prefix="/api", tags=["Autenticação"])
app.include_router(pedidos.router, prefix="/api", tags=["Pedidos & Corridas"])
app.include_router(clientes.router, prefix="/api", tags=["Clientes"])
app.include_router(motoristas.router,
                   prefix="/api/motoristas", tags=["Motoristas"])
app.include_router(servicos.router, prefix="/api",
                   tags=["Serviços de Transfer"])
app.include_router(dashboard.router, prefix="/api",
                   tags=["Painel Administrativo"])
app.include_router(notifications.router, prefix="/api", tags=["Notificações"])
app.include_router(health.router, prefix="/api", tags=["Saúde do Sistema"])
app.include_router(pagamentos.router, prefix="/api/pagamentos",
                   tags=["Mercado Pago & Finanças"])
