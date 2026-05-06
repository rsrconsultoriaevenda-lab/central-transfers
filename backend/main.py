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

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("central-transfers")

app = FastAPI(title="Central Transfers API")

# ==============================
# CORS
# ==============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois restringe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==============================
# DATABASE INIT
# ==============================
@app.on_event("startup")
def startup():
    logger.info("Initializing database...")
    models.Base.metadata.create_all(bind=engine)
    logger.info("Database ready")

    # ==============================
    # ROUTERS (FORA DO STARTUP ✅)
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
    # ROOT
    # ==============================
@app.get("/")
def root():
    return {"status": "ok"}

@app.get("/health")
def health():
    return {"status": "ok"}