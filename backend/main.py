from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import Base, engine, get_db
from backend import models
from backend.routes import whatsapp, servicos, clientes, motoristas, pedidos, auth

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Central Transfers API")

# =============================
# 🔐 CORS
# =============================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================
# 📦 CRIA TABELAS
# =============================
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas do banco de dados criadas/verificadas com sucesso.")
except Exception as e:
    logger.error(f"Erro ao conectar ou criar tabelas no banco de dados: {e}")
    # Em produção, você pode querer que o app falhe aqui ou tente reconectar.

# =============================
# 🔗 ROTAS
# =============================
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(motoristas.router)
app.include_router(servicos.router)
app.include_router(pedidos.router)
app.include_router(whatsapp.router)

# =============================
# 🌱 SEED
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

        db.commit()
        db.refresh(cliente)
        db.refresh(servico)

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
        raise HTTPException(status_code=500, detail=str(e))


    # =============================
    # ❤️ HEALTH CHECK (Verifica a conexão com o banco de dados)
    # =============================
@app.get("/")
def root(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "conectado"
    except Exception:
        db_status = "erro"
    return {
        "status": "online",
        "version": "1.0.0",
        "database": db_status
    }