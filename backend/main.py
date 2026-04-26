import logging
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from backend.routes import (
    whatsapp, servicos, clientes,
    motoristas, pedidos, auth
)
from backend import models
from backend.database import Base, engine, get_db, settings

# Configuração global de logs para exibir erros no terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

app = FastAPI(title="Central Transfers API")

# =============================
# CORS
# =============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip()
                   for origin in settings.ALLOWED_ORIGINS.split(",")],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# DB INIT
# =============================
try:
    # Log de diagnóstico para o deploy
    safe_url = str(engine.url).split("@")[-1]
    logger.info(f"🚀 Iniciando conexão com o driver: {engine.name} em {safe_url}")
    
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Estrutura do banco de dados verificada.")
except Exception as e:
    logger.error(f"❌ Erro crítico de banco de dados: {str(e)}", exc_info=True)

# =============================
# ROUTES
# =============================
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(motoristas.router)
app.include_router(servicos.router)
app.include_router(pedidos.router)
app.include_router(whatsapp.router)

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
    except Exception as e:
        logger.error(f"Falha na conexão com o banco de dados: {str(e)}")
        db_status = "erro"
        current_db = None

    return {  # type: ignore
        "status": "online",
        "version": settings.APP_VERSION,
        "database": db_status,
        "active_schema": current_db
    }

# =============================
# SEED
# =============================


@app.post("/seed")
def seed_database(db: Session = Depends(get_db)):
    try:
        cliente = models.Cliente(
            nome="Cliente Teste",
            telefone="5499999999",
            email="teste@cliente.com"
        )
        db.add(cliente)

        motorista = models.Motorista(
            nome="Motorista Exemplo",
            telefone="5488888888",
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

        db.flush()  # Garante IDs sem fechar a transação

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
            "pedido_id": pedido.id
        }

    except Exception as e:
        db.rollback()
        logger.error(f"💥 Falha no Seed do Banco: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erro no banco: {str(e)}")
