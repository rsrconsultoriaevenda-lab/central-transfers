from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# Importando os roteadores que já existem no seu projeto
from backend.routes import pagamentos, dashboard, whatsapp

# 1. Defina a instância do app no topo do arquivo (Escopo Global)
app = FastAPI(title="Central Transfers API")

# 2. Configure o CORS (Essencial para comunicação com React/Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3. Inclua as rotas dos arquivos que você já criou
app.include_router(pagamentos.router)
app.include_router(dashboard.router)
app.include_router(whatsapp.router)

# 4. Defina a rota de login (ou inclua um router específico de auth se preferir)
# Note que para usar /auth/login sem um roteador separado, definimos o caminho aqui
@app.post("/auth/login", tags=["Autenticação"])
async def login():
    """
    Endpoint de login que o seu frontend irá consumir.
    Certifique-se de que a URL no frontend seja:
    https://central-transfers-production.up.railway.app/auth/login
    """
    return {"message": "Login bem-sucedido", "token": "seu_token_aqui"}

@app.get("/")
async def root():
    return {"status": "online", "service": "Central Transfers"}

# O bloco abaixo é opcional se você usa uvicorn via linha de comando
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
