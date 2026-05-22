from backend.database import SessionLocal
from backend.models import Usuario
from backend.auth import hash_senha

email = 'rsrconsultoriaevenda@gmail.com'
password = 'Ren@220382'

session = SessionLocal()
try:
    user = session.query(Usuario).filter(Usuario.email == email).first()
    if user:
        user.senha_hash = hash_senha(password)
        session.commit()
        print('updated password')
    else:
        print('user not found')
finally:
    session.close()
