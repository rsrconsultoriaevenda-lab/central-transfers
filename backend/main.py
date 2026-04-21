from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from database import Base, engine, get_db
import models

app = FastAPI(title="Central Transfers API")

# 🔥 cria tabelas automaticamente
Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"status": "API rodando 🚀"}


@app.get("/motoristas")
def listar_motoristas(db: Session = Depends(get_db)):
    return db.query(models.Motorista).all()from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # depois você restringe
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)