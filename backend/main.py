import logging
import asyncio
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

# Rotas
from backend.routes import (
    whatsapp, servicos, clientes,
    motoristas, pedidos, auth, pagamentos
)

from backend import models
from backend.database import Base, engine, get_db, SessionLocal

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# APP
# ============================================================
app = FastAPI(title="Central Transfers API", version="1.0.0")

# ============================================================
# CORS (CORRETO PARA PRODUÇÃO)
# ============================================================
origins = [
    "http://localhost:5173",
    "http://localhost:3000",
    "https://central-transfers.vercel.app",
    "https://central-transfers-l9qwmt63s-rsrconsultoriaevenda-labs-projects.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================
# STARTUP
# ============================================================
@app.on_event("startup")
async def startup_event():
    try:
        with engine.begin() as conn:
            Base.metadata.create_all(bind=engine)
            logger.info("✅ Banco sincronizado.")

            # Inicia monitor em background
            asyncio.create_task(monitorar_expiracao_pedidos())

    except Exception as e:
        logger.error(f"Erro no startup: {e}")

        # ============================================================
        # MONITOR DE PEDIDOS
        # ============================================================
async def monitorar_expiracao_pedidos():
    while True:
        try:
            with SessionLocal() as db:
                limite = datetime.now(timezone.utc) - timedelta(minutes=30)

                expirados = db.query(models.Pedido).filter(
                    models.Pedido.status == "AGUARDANDO_PAGAMENTO",
                    models.Pedido.criado_at <= limite
                ).all()

                if expirados:
                    for pedido in expirados:
                        pedido.status = "CANCELADO"

                        db.commit()
                        logger.info(f"Monitor: {len(expirados)} pedidos cancelados.")

        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")

            await asyncio.sleep(300)

            # ============================================================
            # ROUTERS (FORA DO STARTUP — ISSO É CRUCIAL)
            # ============================================================
            app.include_router(auth.router, prefix="/auth", tags=["Auth"])
            app.include_router(clientes.router, prefix="/clientes")
            app.include_router(motoristas.router, prefix="/motoristas")
            app.include_router(servicos.router, prefix="/servicos")
            app.include_router(pedidos.router, prefix="/pedidos")
            app.include_router(whatsapp.router, prefix="/whatsapp")
            app.include_router(pagamentos.router, prefix="/pagamentos")

            # ============================================================
            # ENDPOINTS BASE
            # ============================================================
@app.get("/")
def root():
    return {"message": "Central Transfers API Online 🚀"}

@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok"}

# (Opcional fallback)
@app.post("/login")
async def login_fallback(request: Request, db: Session = Depends(get_db)):
    return await auth.login(db=db, request=request)