import logging
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import engine
from backend import models
from backend.routes import auth, pagamentos, dashboard, whatsapp, motoristas

# ==============================
# CONFIG LOGGING
# ==============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger("central-transfers")

# ==============================
# APP
# ==============================
app = FastAPI(
    title="Central Transfers API",
    version="1.0.0"
)

# ==============================
# ENVIRONMENT
# ==============================
ENV = os.getenv("ENV", "dev")

logger.info(f"Starting API in {ENV} mode")

# ==============================
# CORS CONFIG (Vercel + Local)
# ==============================
if ENV == "dev":
    allow_origins = ["*"]
    allow_origin_regex = None
else:
    allow_origins = [
        "https://central-transfers.vercel.app",
    ]
    # Permite previews da Vercel automaticamente
    allow_origin_regex = r"https://.*vercel.app"

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_origin_regex=allow_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ==============================
    # STARTUP EVENT
    # ==============================
@app.on_event("startup")
def startup_event():
    logger.info("Initializing database...")
    try:
        models.Base.metadata.create_all(bind=engine)
        logger.info("Database ready")
    except Exception as e:
        logger.error(f"Database init error: {e}")

        # ==============================
        # ROUTERS
        # ==============================
        app.include_router(auth.router, prefix="/auth", tags=["Auth"])
        app.include_router(motoristas.router, prefix="/motoristas", tags=["Motoristas"])
        app.include_router(pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])
        app.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
        app.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])

        # ==============================
        # ROOT
        # ==============================
@app.get("/")
def root():
    logger.info("Root endpoint hit")
    return {
"status": "online",
"env": ENV,
"service": "Central Transfers API"
}

# ==============================
# HEALTHCHECK (Railway)
# ==============================
@app.get("/health")
def health():
    return {"status": "ok"}