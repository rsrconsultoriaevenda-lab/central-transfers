import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine
from backend import models
from backend.routes import (
    auth,
    pagamentos,
    dashboard,
    whatsapp,
    motoristas,
    pedidos,
    servicos,
    clientes
)

# ==============================
# LOGGING
# ==============================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("central-transfers")

# ==============================
# APP
# ==============================
app = FastAPI(title="Central Transfers API")

# ==============================
# CORS
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# ROUTERS (FORA DO STARTUP ✔)
# ==============================
app.include_router(auth.router)
app.include_router(motoristas.router)
app.include_router(pagamentos.router)
app.include_router(dashboard.router)
app.include_router(whatsapp.router)
app.include_router(pedidos.router)
app.include_router(servicos.router)
app.include_router(clientes.router)

# ==============================
# STARTUP (SOMENTE BANCO)
# ==============================
@app.on_event("startup")
def startup():
    logger.info("Initializing database...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database ready")

    # ==============================
    # ROOT
    # ==============================
@app.get("/")
def root():
    return {"status": "ok"}

# ==============================
# HEALTH CHECK
# ==============================
@app.get("/health")
def health():
    return {"status": "ok"}