import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importe suas rotas aqui
from backend.routes import auth, motoristas, pedidos, clientes, servicos, dashboard, whatsapp, pagamentos

app = FastAPI(title="Central Transfers API")

# 1. Defina as origens permitidas via Variável de Ambiente (ALLOWED_ORIGINS) ou Lista Padrão
allowed_origins_env = os.getenv("ALLOWED_ORIGINS")
if allowed_origins_env:
    origins = [o.strip() for o in allowed_origins_env.split(",")]
else:
    origins = [
        "http://localhost:5173",
        "http://localhost:5174",
        "https://central-transfers.vercel.app"
    ]

# 2. Adicione o Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,           # Lista de domínios permitidos
    allow_credentials=True,          # Permite envio de cookies/auth headers
    # Permite todos os métodos (GET, POST, PUT, DELETE)
    allow_methods=["*"],
    allow_headers=["*"],             # Permite todos os cabeçalhos
)

# Incluir as rotas
app.include_router(auth.router)
app.include_router(motoristas.router)
app.include_router(pedidos.router)
app.include_router(clientes.router)
app.include_router(servicos.router)
app.include_router(dashboard.router)
app.include_router(whatsapp.router)
app.include_router(pagamentos.router)


@app.get("/health")
def health_check():
    return {"status": "online"}
