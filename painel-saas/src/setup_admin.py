from database import SessionLocal
from models import Usuario
from auth import hash_senha

def criar_admin_mestre():
    db = SessionLocal()
    email = "admin@centraltransfers.com"
    senha_plana = "Master@2024" # Altere após o primeiro acesso
    
    # Verifica se já existe
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    
    if usuario:
        usuario.senha = hash_senha(senha_plana)
        usuario.role = "admin"
        print(f"✅ Usuário {email} atualizado! Senha: {senha_plana}")
    else:
        novo_admin = Usuario(email=email, senha=hash_senha(senha_plana), role="admin")
        db.add(novo_admin)
        print(f"🚀 Admin Mestre criado! Login: {email} | Senha: {senha_plana}")
    
    db.commit()
    db.close()

if __name__ == "__main__":
    criar_admin_mestre()