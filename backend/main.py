from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import auth, pagamentos, dashboard, whatsapp

app = FastAPI(title="Central Transfers API")

# CORS
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

# ROUTERS
app.include_router(auth.router)
app.include_router(pagamentos.router)
app.include_router(dashboard.router)
app.include_router(whatsapp.router)

@app.get("/")
def root():
    return {"status": "online"}

@app.get("/health")
def health():
    return {"status": "ok"}