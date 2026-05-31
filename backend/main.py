import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.config import settings
from backend.services.notifier_service import notifier

from backend.routes import (auth, pedidos, clientes, motoristas, servicos,
                            dashboard, pagamentos, notifications, health, whatsapp)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Central Transfers inicializado com sucesso!")
    yield
    logger.info("🛑 Encerrando conexões com segurança...")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CentralTransfers")

app = FastAPI(
    title="Central Transfers API",
    description="Backend de logística para gestão de transfers Aeroporto POA / Gramado",
    lifespan=lifespan,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.state.notifier = notifier


def setup_origins():
    raw_origins = getattr(settings, "ALLOWED_ORIGINS", "")
    if raw_origins and raw_origins.strip() == "*":
        return ["*"]

    # URLs padrão de desenvolvimento e produção fixa
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://central-transfers.vercel.app",
    ]

    # Adiciona origens extras vindas do arquivo .env ou do painel do Render
    if raw_origins:
        extra_origins = [o.strip()
                         for o in raw_origins.split(",") if o.strip()]
        for o in extra_origins:
            if o not in origins:
                origins.append(o)
    return origins


origins = setup_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/api/docs")

# 1️⃣ Mapeamento Direto (Compatibilidade com Storefront e App do Motorista)
app.include_router(auth.router, tags=["Autenticação"])
app.include_router(pedidos.router, tags=["Pedidos & Corridas"])
app.include_router(clientes.router, tags=["Clientes"])
app.include_router(motoristas.router, tags=["Motoristas"])
app.include_router(servicos.router, tags=["Serviços de Transfer"])
app.include_router(dashboard.router, tags=["Painel Administrativo"])
app.include_router(whatsapp.router, tags=["WhatsApp"])
app.include_router(notifications.router, tags=["Notificações"])
app.include_router(health.router, tags=["Saúde do Sistema"])
app.include_router(pagamentos.router, tags=["Pagamentos & Checkout"])

# 2️⃣ Mapeamento com /api (Otimizado para Proxy Vercel)
app.include_router(auth.router, prefix="/api", tags=["Autenticação"])
app.include_router(pedidos.router, prefix="/api", tags=["Pedidos & Corridas"])
app.include_router(clientes.router, prefix="/api", tags=["Clientes"])
app.include_router(motoristas.router, prefix="/api", tags=["Motoristas"])
app.include_router(servicos.router, prefix="/api",
                   tags=["Serviços de Transfer"])
app.include_router(dashboard.router, prefix="/api",
                   tags=["Painel Administrativo"])
app.include_router(whatsapp.router, prefix="/api", tags=["WhatsApp"])
app.include_router(notifications.router, prefix="/api", tags=["Notificações"])
app.include_router(health.router, prefix="/api", tags=["Saúde do Sistema"])
app.include_router(pagamentos.router, prefix="/api",
                   tags=["Pagamentos & Checkout"])
