import sys
import os

# Adiciona o diretório atual ao path para importar o backend
sys.path.append(os.getcwd())

from backend.database import SessionLocal
from backend.models import Motorista
from backend.services.push_service import send_web_push

def disparar_teste_vibracao(motorista_id):
    db = SessionLocal()
    try:
        motorista = db.query(Motorista).filter(Motorista.id == motorista_id).first()
        
        if not motorista or not motorista.push_token:
            print(f"❌ Erro: Motorista ID {motorista_id} não encontrado ou ainda não aceitou notificações no celular.")
            return

        print(f"🚀 Enviando Push de teste para {motorista.nome}...")
        
        data = {
            "title": "🚨 TESTE DE EMERGÊNCIA",
            "body": "Se o seu celular vibrou, a Central Transfers está operando 100%!",
            "vibrate": [500, 110, 500, 110, 450, 110, 200, 110, 170, 40, 450, 110, 200, 110, 170, 40] # Ritmo de alerta
        }

        sucesso = send_web_push(motorista.push_token, data)
        
        if sucesso:
            print("✅ Notificação enviada! Verifique o celular do motorista.")
        else:
            print("⚠️ Falha ao entregar. O navegador pode ter invalidado o token.")
            
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python test_push_manual.py [ID_DO_MOTORISTA]")
    else:
        disparar_teste_vibracao(int(sys.argv[1]))