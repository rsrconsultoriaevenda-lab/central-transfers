import logging
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

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
from backend.database import Base, engine, get_db, settings, SessionLocal

# =============================
# CONFIGURAÇÃO DE LOGGING
# =============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =============================
# TAREFAS EM SEGUNDO PLANO
# =============================
async def monitorar_expiracao_pedidos():
    while True:
        try:
            with SessionLocal() as db:
                limite = datetime.utcnow() - timedelta(minutes=30)
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        with engine.begin() as conn:
            Base.metadata.create_all(bind=engine)
            conn.execute(text("ALTER TABLE motoristas ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ATIVO';"))
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS criado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS valor_comissao DECIMAL(10,2) DEFAULT 0.0;"))
            logger.info("✅ Banco de dados sincronizado.")
    except Exception as e:
        logger.warning(f"⚠️ Nota de Migração: {e}")

        bg_task = asyncio.create_task(monitorar_expiracao_pedidos())
        yield
        bg_task.cancel()

        # ============================================================
        # INICIALIZAÇÃO GLOBAL (IMPORTANTE: SEM ESPAÇOS NO INÍCIO)
        # ============================================================
        app = FastAPI(
            title="Central Transfers API",
            version="0.1.0",
            lifespan=lifespan
        )

        # =============================
        # CONFIGURAÇÃO DE CORS (SOLUÇÃO PARA O ERRO)
        # =============================
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Libera todas as origens para resolver o erro do PowerShell
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
            expose_headers=["*"]
        )

        # =============================
        # REGISTRO DE ROTAS
        # =============================
        app.include_router(auth.router, tags=["Autenticação"])
        app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
        app.include_router(motoristas.router, prefix="/motoristas", tags=["Motoristas"])
        app.include_router(servicos.router, prefix="/servicos", tags=["Serviços"])
        app.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
        app.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
        app.include_router(pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])

        # Endpoints de sistema
@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1")).fetchone()
    return {"status": "online", "db": "healthy"}