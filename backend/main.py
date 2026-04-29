import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta

# Importações internas
from backend.routes import (
    whatsapp, servicos, clientes,
    motoristas, pedidos, auth, pagamentos
)
from backend import models
from backend.database import Base, engine, get_db, settings, SessionLocal
from backend.auth import hash_senha

# =============================
# LOGGING
# =============================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# =============================
# BACKGROUND TASK
# =============================


async def monitorar_expiracao_pedidos():
    while True:
        logger.info("🔍 Checando pedidos expirados...")
        try:
            with SessionLocal() as db:
                limite = datetime.utcnow() - timedelta(minutes=30)
                expirados = db.query(models.Pedido).filter(
                    models.Pedido.status == "AGUARDANDO_PAGAMENTO",
                    models.Pedido.criado_at <= limite
                ).all()

                for pedido in expirados:
                    pedido.status = "CANCELADO"
                    logger.info(
                        f"🚫 Pedido #{pedido.id} cancelado por expiração")
                db.commit()
        except Exception as e:
            logger.error(f"Erro no monitoramento de pedidos: {e}")
        await asyncio.sleep(300)  # Checa a cada 5 minutos


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização do Banco de Dados
    try:
        with engine.connect() as conn:
            Base.metadata.create_all(bind=engine)
            conn.execute(text(
                "ALTER TABLE motoristas ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ATIVO';"))
            conn.execute(text(
                "ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS criado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            conn.execute(text(
                "ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS valor_comissao DECIMAL(10,2) DEFAULT 0.0;"))
            conn.commit()
            logger.info("✅ Banco de dados conectado e tabelas verificadas")
    except Exception as e:
        logger.error(
            f"🚨 Erro ao verificar tabelas (pode ser normal se já existirem): {e}")

    # Inicia tarefa em segundo plano
    task = asyncio.create_task(monitorar_expiracao_pedidos())
    yield
    task.cancel()

# =============================
# APP CONFIGURATION
# =============================
app = FastAPI(
    title="Central Transfers API",
    version="0.1.0",
    lifespan=lifespan
)

# =============================
# CORS
# =============================
allowed_origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(
    ",")] if settings.ALLOWED_ORIGINS else ["*"]
logger.info(f"CORS: Origens permitidas: {allowed_origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True if "*" not in allowed_origins else False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de Rotas - Removido prefixo redundante do WhatsApp
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(motoristas.router)
app.include_router(servicos.router)
app.include_router(pedidos.router)
app.include_router(whatsapp.router)  # Router já tem prefixo /whatsapp
app.include_router(pagamentos.router)

# =============================
# WEBHOOK WHATSAPP (META ENTRY POINT)
# =============================


@app.get("/webhook")
async def verify_webhook(request: Request):
    """Endpoint de verificação para o handshake da Meta API."""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(content="forbidden", status_code=403)


@app.post("/webhook")
async def webhook_incoming(request: Request, background_tasks: BackgroundTasks):
    data = await request.json()
    background_tasks.add_task(whatsapp.processar_evento_whatsapp, data)
    return {"status": "ok"}


@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    try:
        # Tenta uma operação simples no banco
        db.execute(text("SELECT 1")).fetchone()
        return {
            "status": "online",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503, detail="Database connection failed")
