from fastapi import FastAPI
from backend.routes import auth
app.include_router(auth.router)

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}