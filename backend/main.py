import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

# Importações internas
from backend.routes import (
    whatsapp, servicos, clientes,
    motoristas, pedidos, auth, pagamentos
)
from backend import models
from backend.database import Base, engine, get_db, SessionLocal
from backend.config import settings

# 1. LOGGING
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# ============================================================
# 2. INICIALIZAÇÃO DO APP (MANTIDA NO TOPO PARA EVITAR NAMEERROR)
# ============================================================
app = FastAPI(title="Central Transfers API", version="0.1.0")

# 3. CONFIGURAÇÃO DE CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. MONITOR DE PEDIDOS (TASK DE BACKGROUND)
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
                        logger.info(f"Monitor: {len(expirados)} pedidos expirados cancelados.")
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
            await asyncio.sleep(300)

            # 5. LIFESPAN (EVENTOS DE INICIALIZAÇÃO)
@app.on_event("startup")
async def startup_event():
    try:
        with engine.begin() as conn:
            Base.metadata.create_all(bind=engine)
            # Alterações seguras para SQLite/MySQL
            try:
                conn.execute(text("ALTER TABLE motoristas ADD COLUMN status VARCHAR(50) DEFAULT 'ATIVO';"))
            except Exception: pass
            try:
                conn.execute(text("ALTER TABLE pedidos ADD COLUMN criado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            except Exception: pass
            logger.info("✅ Banco sincronizado.")
    except Exception as e:
        logger.warning(f"Aviso Startup: {e}")

        asyncio.create_task(monitorar_expiracao_pedidos())

        # 6. REGISTRO DE ROUTERS
        app.include_router(auth.router)
        app.include_router(clientes.router)
        app.include_router(motoristas.router)
        app.include_router(servicos.router)
        app.include_router(pedidos.router)
        app.include_router(whatsapp.router)
        app.include_router(pagamentos.router)

        # 7. ENDPOINTS GLOBAIS
@app.post("/login", tags=["Autenticação"])
async def login_fallback(request: Request, db: Session = Depends(get_db)):
    return await auth.login(db=db, request=request)

@app.get("/", tags=["Sistema"])
def read_root():
    return {"message": "Central Transfers API Online", "status": "online"}

@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1")).fetchone()
    return {"status": "healthy"}