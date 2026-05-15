from backend.database import SessionLocal
from backend.models import Usuario
from backend.auth import verificar_senha

db = SessionLocal()

user = db.query(Usuario).filter(
    Usuario.email == "rsrconsultoriaevenda@gmail.com"
).first()

print("USUARIO:", user)

if user:
    print("EMAIL:", user.email)
    print("HASH:", user.senha)
    print(
        "SENHA OK:",
        verificar_senha("Ren@220382", user.senha)
    )