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

                for pedido in expirados:
                    pedido.status = "CANCELADO"
                    logger.info(f"🚫 Pedido #{pedido.id} cancelado automaticamente.")

                    if expirados:
                        db.commit()
        except Exception as e:
            logger.error(f"🚨 Erro no monitoramento: {e}")

            await asyncio.sleep(300)  # Executa a cada 5 minutos

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Inicialização ---
    try:
        with engine.begin() as conn:
            # Cria tabelas se não existirem
            Base.metadata.create_all(bind=engine)

            # Migrações manuais de segurança (Colunas dinâmicas)
            conn.execute(text("ALTER TABLE motoristas ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ATIVO';"))
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS criado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            conn.execute(text("ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS valor_comissao DECIMAL(10,2) DEFAULT 0.0;"))

            logger.info("✅ Banco de dados sincronizado e pronto.")
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
            # CONFIGURAÇÃO DE CORS (Crucial para Vercel)
            # =============================
            raw_origins = settings.ALLOWED_ORIGINS.split(",") if settings.ALLOWED_ORIGINS else []
            allowed_origins = [o.strip() for o in raw_origins if o.strip()]

            # Se a lista estiver vazia, define padrões de segurança em vez de "*" puro
            if not allowed_origins:
                allowed_origins = ["http://localhost:5173"]

                # Adiciona explicitamente o domínio da Vercel (opcional, mas recomendado)
                # allowed_origins.append("https://central-transfers.vercel.app")

                app.add_middleware(
                    CORSMiddleware,
                    allow_origins=allowed_origins,
                    allow_credentials=True,
                    allow_methods=["*"],
                    allow_headers=["*"],
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

                # =============================
                # WEBHOOK WHATSAPP (META API)
                # =============================
@app.get("/webhook")
async def verify_webhook(request: Request):
    """Handshake de verificação da Meta."""
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        logger.info("✅ Webhook verificado com sucesso!")
        return PlainTextResponse(content=challenge)

    return PlainTextResponse(content="forbidden", status_code=403)

@app.post("/webhook")
async def webhook_incoming(request: Request, background_tasks: BackgroundTasks):
    """Recebe mensagens em tempo real do WhatsApp."""
    data = await request.json()
    background_tasks.add_task(whatsapp.processar_evento_whatsapp, data)
    return {"status": "ok"}

# =============================
# MONITORAMENTO DE SAÚDE
# =============================
@app.get("/health", tags=["Sistema"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1")).fetchone()
        return {
    "status": "online",
    "db_connection": "healthy",
    "timestamp": datetime.now().isoformat()
}
    except Exception as e:
        logger.critical(f"Health check falhou: {e}")
        raise HTTPException(status_code=503, detail="Service Unavailable")