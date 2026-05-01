import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# IMPORTAÇÃO DAS ROTAS (ROOT = /backend no Railway)
from routes import auth, pagamentos, dashboard, whatsapp

# APP FASTAPI
app = FastAPI(title="Central Transfers API")

# CORS (produção + local)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://central-transfers.vercel.app",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROTAS
app.include_router(auth.router)
app.include_router(pagamentos.router)
app.include_router(dashboard.router)
app.include_router(whatsapp.router)

# ROOT
@app.get("/")
def root():
    return {"status": "online"}

# HEALTHCHECK (Railway)
@app.get("/health")
def health():
    return {"status": "ok"}