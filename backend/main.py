import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
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

# 1. Configuração de Log
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# 2. Monitor de Pedidos (Background)
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
        except Exception as e:
            logger.error(f"Erro no monitoramento: {e}")
            await asyncio.sleep(300)

            # 3. Ciclo de Vida (Lifespan)
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.begin() as conn:
            Base.metadata.create_all(bind=engine)
            conn.execute(text("ALTER TABLE motoristas ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ATIVO';"))
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS criado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            logger.info("✅ Banco sincronizado.")
    except Exception as e:
        logger.warning(f"Nota: {e}")
        bg_task = asyncio.create_task(monitorar_expiracao_pedidos())
        yield
        bg_task.cancel()

        # ============================================================
        # 4. INICIALIZAÇÃO DO APP (MANTENHA ESTA ORDEM)
        # ============================================================
        app = FastAPI(title="Central Transfers API", version="0.1.0", lifespan=lifespan)

        # 5. MIDDLEWARE DE CORS (LIBERA O FRONTEND)
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # 6. REGISTRO DE ROTAS
        app.include_router(auth.router)
        app.include_router(clientes.router)
        app.include_router(motoristas.router)
        app.include_router(servicos.router)
        app.include_router(pedidos.router)
        app.include_router(whatsapp.router)
        app.include_router(pagamentos.router)

        # 7. ENDPOINTS GLOBAIS
@app.get("/", tags=["Sistema"])
def read_root():
    return {"message": "Central Transfers API Online", "status": "online"}

@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1")).fetchone()
    return {"status": "healthy"}

@app.post("/login", tags=["Autenticação"])(auth.login)