import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timedelta

from backend.routes import (
    whatsapp, servicos, clientes,
    motoristas, pedidos, auth, pagamentos
)
from backend import models
from backend.database import Base, engine, get_db, settings, SessionLocal
from backend.auth import hash_senha

# Configuração global de logs para exibir erros no terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# =============================
# BACKGROUND TASK: MONITORAMENTO DE PAGAMENTOS
# =============================


async def monitorar_expiracao_pedidos():
    """Tarefa que roda periodicamente para cancelar pedidos não pagos."""
    while True:
        logger.info("🔍 Iniciando checagem de pedidos expirados...")
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
                        f"🚫 Pedido #{pedido.id} cancelado por Timeout.")

                db.commit()
        except Exception as e:
            logger.error(f"⚠️ Erro na monitoração (aguardando retry): {e}")

        # Aguarda 60 segundos entre checagens para evitar loop infinito
        await asyncio.sleep(60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # =============================
    # DB INIT & MIGRATIONS
    # =============================
    try:
        # Usamos engine.connect() em vez de begin() para evitar travar o boot em caso de erro
        with engine.connect() as conn:
            Base.metadata.create_all(bind=engine)
            # Migrações manuais rápidas
            conn.execute(text(
                "ALTER TABLE motoristas ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'ATIVO';"))
            conn.execute(text(
                "ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS criado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;"))
            conn.execute(text(
                "ALTER TABLE pedidos ADD COLUMN IF NOT EXISTS valor_comissao DECIMAL(10, 2) DEFAULT 0.0;"))
            conn.commit()
            logger.info(
                "✅ Conexão com banco de dados estabelecida e tabelas verificadas.")
    except Exception as e:
        # O app NÃO morre se o banco falhar, ele apenas loga o erro.
        # Isso permite que o deploy termine e você veja o erro nos logs do Health Check.
        logger.critical(f"🚨 FALHA NA CONEXÃO COM BANCO: {e}")

    # Inicia tarefa de monitoramento
    task = asyncio.create_task(monitorar_expiracao_pedidos())
    yield
    task.cancel()

app = FastAPI(title="Central Transfers API", lifespan=lifespan)

# =============================
# CORS
# =============================

allowed_origins = [origin.strip() 
                   for origin in settings.ALLOWED_ORIGINS.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    # Senior Fix: Browsers bloqueiam '*' com credentials=True.
    # Se a origem for '*', desativamos credentials para permitir o fetch.
    allow_credentials=True if "*" not in allowed_origins else False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# =============================
# ROUTES
# =============================
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(motoristas.router)
app.include_router(servicos.router)
app.include_router(pedidos.router)
app.include_router(whatsapp.router)
app.include_router(pagamentos.router)

# =============================
# HEALTH CHECK
# =============================


@app.get("/")
def root(db: Session = Depends(get_db)):
    try:
        # Verifica a conexão e obtém o nome do banco atual
        # Suporta tanto MySQL (DATABASE()) quanto PostgreSQL (current_database())
        if "postgresql" in str(engine.url):
            current_db = db.execute(text("SELECT current_database()")).scalar()
        else:
            current_db = db.execute(text("SELECT DATABASE()")).scalar()
        db_status = "conectado"

        # Verifica se há motoristas ativos
        motoristas_count = db.execute(
            text("SELECT COUNT(*) FROM motoristas WHERE status = 'ATIVO'")).scalar()
    except Exception as e:
        error_detail = str(e)
        logger.error(f"Falha na conexão com o banco de dados: {error_detail}")
        db_status = f"erro: {error_detail[:50]}..."
        current_db = None
        motoristas_count = 0

    return {  # type: ignore
        "status": "online",
        "version": settings.APP_VERSION,
        "database": db_status,
        "active_schema": current_db,
        "health": {
            "db_connected": db_status == "conectado",
            "active_drivers": motoristas_count
        }
    }

# =============================
# SEED
# =============================


@app.post("/seed")
def seed_database(db: Session = Depends(get_db)):
    # Senior Fix: Evita que o seed seja rodado em produção acidentalmente
    # Se a URL do banco não contiver 'localhost' ou '127.0.0.1', bloqueia (opcional)
    # if "localhost" not in settings.DB_HOST and "127.0.0.1" not in settings.DB_HOST:
    #     raise HTTPException(status_code=403, detail="Seed permitido apenas em ambiente de desenvolvimento.")

    try:
        # 1. Criar um Usuário Administrador para Login
        admin_existente = db.query(models.Usuario).filter(
            models.Usuario.email == "admin@teste.com").first()
        if not admin_existente:
            admin = models.Usuario(
                email="admin@teste.com",
                senha=hash_senha("admin123"),
                role="admin"
            )
            db.add(admin)
            logger.info("👤 Usuário admin criado para testes.")

        # 2. Criar Cliente
        cliente = models.Cliente(
            nome="Cliente Teste",
            telefone="5554999999999",
            email="teste@cliente.com"
        )
        db.add(cliente)

        motorista = models.Motorista(
            nome="Motorista Exemplo",
            telefone="5554888888888",
            carro="Sedan",
            placa="ABC-1234",
            modelo="Corolla",
            ano=2023,
            status="ATIVO"
        )
        db.add(motorista)

        servico = models.Servico(
            nome="Transfer POA x Gramado",
            tipo="TRANSFER",
            descricao="Transfer de luxo",
            ativo=True
        )
        db.add(servico)

        db.flush()

        pedido = models.Pedido(
            cliente_id=cliente.id,
            servico_id=servico.id,
            origem="Aeroporto Salgado Filho",
            destino="Hotel Serra Azul",
            data_servico=datetime.now(),
            valor=250.00,
            status="PENDENTE"
        )

        db.add(pedido)
        db.commit()

        return {
            "msg": "Banco populado com sucesso!",
            "pedido_id": pedido.id,
            "login_teste": "admin@teste.com / admin123"
        }

    except Exception as e:
        db.rollback()
        logger.error(f"💥 Falha no Seed do Banco: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")


@app.get("/webhook")
async def verify_webhook(request: Request):
    hub_mode = request.query_params.get("hub.mode")
    hub_token = request.query_params.get("hub.verify_token")
    hub_challenge = request.query_params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=hub_challenge)

    return {"error": "Token inválido"}


@app.post("/webhook")
async def whatsapp_webhook(request: Request):
    data = await request.json()
    logger.info(f"📩 Webhook recebido: {data}")
    return {"status": "ok"}
