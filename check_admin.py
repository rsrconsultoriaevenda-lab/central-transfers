from backend.database import SessionLocal
from backend.models import Usuario
from backend.auth import verificar_senha

email = 'rsrconsultoriaevenda@gmail.com'
password = 'Ren@220382'

sess = SessionLocal()
user = sess.query(Usuario).filter(Usuario.email == email).first()
if not user:
    print('NO_USER')
else:
    print('FOUND', user.email, user.role, 'hash=', user.senha_hash[:60])
    try:
        ok = verificar_senha(password, user.senha_hash)
        print('PASSWORD_OK', ok)
    except Exception as e:
        print('VERIFY_ERROR', type(e).__name__, e)
sess.close()
