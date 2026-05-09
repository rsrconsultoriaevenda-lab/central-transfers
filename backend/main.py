import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import settings  # Caminho absoluto para evitar erro de import
from backend.database import engine
from backend import models
from backend.routes import (
    auth, pagamentos, dashboard, whatsapp,
    motoristas, pedidos, servicos, clientes
)

# Configuração de Log
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("central-transfers")

app = FastAPI(title="Central Transfers API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTERS (Mantenha fora do startup)
app.include_router(auth.router)
app.include_router(motoristas.router)
app.include_router(pagamentos.router)
app.include_router(dashboard.router)
app.include_router(whatsapp.router)
app.include_router(pedidos.router)
app.include_router(servicos.router)
app.include_router(clientes.router)

# DATABASE INIT
@app.on_event("startup")
def startup():
    logger.info("Initializing database...")
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database ready")
    except Exception as e:
        logger.error(f"Database error: {e}")

        # ROTAS GLOBAIS (CORRIGIDAS: Identação para a esquerda!)
@app.get("/")
def root():
    return {"status": "ok", "message": "Central Transfers API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}