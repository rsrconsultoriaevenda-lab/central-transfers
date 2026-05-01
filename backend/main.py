import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.database import engine
from backend import models

# IMPORTAÇÃO DAS ROTAS (Usando o prefixo backend para garantir compatibilidade com o Dockerfile)
from backend.routes import auth, pagamentos, dashboard, whatsapp, motoristas

# CRIAÇÃO AUTOMÁTICA DE TABELAS
# Isso garante que o banco Aiven receba as tabelas Pedido, Motorista, etc. no primeiro deploy
models.Base.metadata.create_all(bind=engine)

# APP FASTAPI
app = FastAPI(title="Central Transfers API")

# Configuração de CORS para permitir acesso do Painel Vercel e Local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REGISTRO DOS ROUTERS
app.include_router(auth.router)
app.include_router(pagamentos.router)
app.include_router(dashboard.router)
app.include_router(whatsapp.router)
app.include_router(motoristas.router)

# ROOT
@app.get("/")
def root():
    return {"status": "online", "message": "Central Transfers API is running"}

# HEALTHCHECK (Obrigatório para o Railway e configurado no railway.json)
@app.get("/health")
def health():
    return {"status": "ok"}