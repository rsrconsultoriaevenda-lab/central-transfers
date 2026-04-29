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
    """Cancela pedidos que não foram pagos após 30 minutos."""
    while True:
        try:
            logger.info("🔍 [Background] Checando pedidos expirados...")
            with SessionLocal() as db:
                limite = datetime.utcnow() - timedelta(minutes=30)
                expirados = db.query(models.Pedido).filter(
                    models.Pedido.status == "AGUARDANDO_PAGAMENTO",
                    models.Pedido.criado_at <= limite
                ).all()

                if expirados:
                    for pedido in expirados:
                        pedido.status = "CANCELADO"
                        logger.info(f"🚫 Pedido #{pedido.id} cancelado automaticamente.")
                        db.commit()
        except Exception as e:
            logger.error(f"🚨 Erro no monitoramento: {e}")

            await asyncio.sleep(300)  # Checa a cada 5 minutos

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Inicialização do Banco ---
    try:
        with engine.begin() as conn:
            Base.metadata.create_all(bind=engine)
            # Garantia de colunas (Migrações rápidas)
            conn.execute(text("ALTER TABLE motoristas ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ATIVO';"))
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS criado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS valor_comissao DECIMAL(10,2) DEFAULT 0.0;"))
            logger.info("✅ Banco de dados sincronizado.")
    except Exception as e:
        logger.warning(f"⚠️ Nota de Migração: {e}")

        # Inicia tarefa em background
        bg_task = asyncio.create_task(monitorar_expiracao_pedidos())
        yield
        # --- Desligamento ---
        bg_task.cancel()
        try:
            await bg_task
        except asyncio.CancelledError:
            logger.info("🛑 Background task finalizada.")

            # =============================
            # INICIALIZAÇÃO DO APP
            # =============================
            app = FastAPI(
                title="Central Transfers API",
                version="0.1.0",
                lifespan=lifespan
            )

            # =============================
            # CONFIGURAÇÃO DE CORS (MODO COMPATÍVEL)
            # =============================
            # Usando "*" temporariamente para garantir que a Vercel conecte
            app.add_middleware(
                CORSMiddleware,
                allow_origins=["*"],
                allow_credentials=True,
                allow_methods=["*"],
                allow_headers=["*"],
                expose_headers=["*"]
            )

            # =============================
            # REGISTRO DE ROTAS
            # =============================
            # As rotas DEVEM ficar fora de qualquer função para serem registradas no app
            app.include_router(auth.router, tags=["Autenticação"])
            app.include_router(clientes.router, prefix="/clientes", tags=["Clientes"])
            app.include_router(motoristas.router, prefix="/motoristas", tags=["Motoristas"])
            app.include_router(servicos.router, prefix="/servicos", tags=["Serviços"])
            app.include_router(pedidos.router, prefix="/pedidos", tags=["Pedidos"])
            app.include_router(whatsapp.router, prefix="/whatsapp", tags=["WhatsApp"])
            app.include_router(pagamentos.router, prefix="/pagamentos", tags=["Pagamentos"])

            # =============================
            # ENDPOINTS GLOBAIS / WEBHOOKS
            # =============================
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=params.get("hub.challenge"))
    return PlainTextResponse(content="forbidden", status_code=403)

@app.post("/webhook")
async def webhook_incoming(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    background_tasks.add_task(whatsapp.processar_evento_whatsapp, data)
    return {"status": "ok"}

@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1")).fetchone()
        return {
    "status": "online",
    "db": "healthy",
    "server_time": datetime.now().isoformat()
}
    except Exception as e:
        logger.critical(f"Health check falhou: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")