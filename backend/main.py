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

# Configuração básica de log
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

app = FastAPI(title="Central Transfers API")

# Configura as origens permitidas (URLs do Vercel)
allowed_origins_raw = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in allowed_origins_raw.split(",")]

# Para JWT funcionar com allow_credentials=True, ALLOWED_ORIGINS NÃO PODE ser "*".
# O usuário DEVE configurar ALLOWED_ORIGINS no Render com as URLs reais dos frontends.
# Se ALLOWED_ORIGINS não for definido ou for "*", o navegador bloqueará a requisição.
# Vamos assumir que ALLOWED_ORIGINS será configurado corretamente em produção.


app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins, # Deve ser uma lista de URLs específicas em produção
    allow_credentials=True,        # Necessário para JWT nos headers
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup_event():
    """Automação de Inicialização: Cria admin e sementes se o banco estiver vazio."""
    try:
        # Cria tabelas se não existirem
        models.Base.metadata.create_all(bind=engine)
    except Exception as e:
        logging.error(f"❌ Erro ao criar tabelas: {e}")

    db = SessionLocal()
    try:
        # 1. Garantir Usuário Admin Padrão
        admin = db.query(models.Usuario).filter(models.Usuario.username == "admin").first()
        if not admin:
            logging.info("🤖 Automação: Criando usuário administrador padrão (admin)...")
            hashed_pwd = pwd_context.hash("admin123")
            default_admin = models.Usuario(
                username="admin", hashed_password=hashed_pwd)
            db.add(default_admin)
            try:
                db.commit()
                logging.info("✅ Admin criado com sucesso!")
            except Exception:
                db.rollback()

        # 2. Garantir Serviços Iniciais
        # Usando text() para compatibilidade absoluta com Postgres/MySQL
        services_exist = db.execute(
            text("SELECT 1 FROM servicos LIMIT 1")).first()
        if not services_exist:
            logging.info("🤖 Automação: Populando serviços iniciais...")
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
        logging.error(f"❌ Erro na automação de inicialização: {e}")
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
