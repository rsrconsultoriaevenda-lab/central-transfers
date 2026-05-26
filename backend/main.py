import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from backend.config import settings
from backend.services.notifier_service import notifier

from backend.routes import (auth, pedidos, clientes, motoristas, servicos,
                            dashboard, pagamentos, notifications, health)


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

raw_origins = getattr(settings, "ALLOWED_ORIGINS", "")
if raw_origins and raw_origins.strip() == "*":
    origins = ["*"]
else:
    env_origins = [o.strip() for o in raw_origins.split(",")
                   if o.strip()] if raw_origins else []
    origins = env_origins + [
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


@app.get("/", include_in_schema=False)
async def root_redirect():
    return RedirectResponse(url="/api/docs")

# Mapeamento de rotas prefixadas com /api para compatibilidade com Vercel/Proxy
app.include_router(auth.router, prefix="/api/auth", tags=["Autenticação"])
app.include_router(pedidos.router, prefix="/api/pedidos",
                   tags=["Pedidos & Corridas"])
app.include_router(clientes.router, prefix="/api/clientes", tags=["Clientes"])
app.include_router(motoristas.router,
                   prefix="/api/motoristas", tags=["Motoristas"])
app.include_router(servicos.router, prefix="/api/servicos",
                   tags=["Serviços de Transfer"])
app.include_router(dashboard.router, prefix="/api/dashboard",
                   tags=["Painel Administrativo"])
app.include_router(notifications.router,
                   prefix="/api/notifications", tags=["Notificações"])
app.include_router(health.router, prefix="/api/health",
                   tags=["Saúde do Sistema"])
app.include_router(pagamentos.router, prefix="/api",
                   tags=["Pagamentos & Checkout"])
