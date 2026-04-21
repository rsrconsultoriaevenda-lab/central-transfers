from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from backend.routes import clientes, motoristas, servicos, pedidos, whatsapp
from backend import auth, models, schemas
from backend.database import engine, get_db, SessionLocal
import os
import logging
from backend.auth import pwd_context
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI(title="Central Transfers API")

# Configura as origens permitidas (URLs do Vercel)
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",")]

# Se ALLOWED_ORIGINS for '*', não podemos usar allow_credentials=True
# Esta lógica ajusta automaticamente para evitar o erro "Failed to fetch"
allow_all = "*" in allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all else allowed_origins,
    allow_credentials=not allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

# cria tabelas automaticamente
models.Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup_event():
    """Automação de Inicialização: Cria admin e sementes se o banco estiver vazio."""
    db = SessionLocal()
    try:
        # 1. Garantir Usuário Admin Padrão
        admin_exists = db.query(models.Usuario).first()
        if not admin_exists:
            print("🤖 Automação: Criando usuário administrador padrão...")
            hashed_pwd = pwd_context.hash("admin123")
            default_admin = models.Usuario(
                username="admin", hashed_password=hashed_pwd)
            db.add(default_admin)
            try:
                db.commit()
            except Exception:
                db.rollback()

        # 2. Garantir Serviços Iniciais
        # Usando text() para compatibilidade absoluta com Postgres/MySQL
        services_exist = db.execute(
            text("SELECT 1 FROM servicos LIMIT 1")).first()
        if not services_exist:
            print("🤖 Automação: Populando serviços iniciais...")
            servicos_iniciais = [
                {"nome": "Tour Gramado", "tipo": "Tour",
                    "descricao": "Passeio pelos principais pontos turísticos."},
                {"nome": "Transfer Aeroporto", "tipo": "Transfer",
                    "descricao": "Transporte privativo Aeroporto POA."},
                {"nome": "Carro a disposição", "tipo": "Carro à disposição",
                    "descricao": "Motorista privativo por 8h."}
            ]
            for s in servicos_iniciais:
                db.add(models.Servico(**s))
            db.commit()

    except Exception as e:
        print(f"❌ Erro na automação de inicialização: {e}")
    finally:
        db.close()


app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(motoristas.router)
app.include_router(servicos.router)
app.include_router(pedidos.router)
app.include_router(whatsapp.router)


@app.get("/")
def home(db: Session = Depends(get_db)):
    try:
        # Teste simples de conexão com o banco
        db.execute(text("SELECT 1")).first()
        db_status = "conectado"
    except Exception:
        db_status = "erro de conexão"

    return {
        "status": "online",
        "version": "1.0.0-prod",
        "database": db_status,
        "environment": os.getenv("RENDER", "local"),
        "allowed_origins": allowed_origins if allowed_origins_raw != "*" else "all"
    }
