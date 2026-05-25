from backend.services.notifier_service import notifier
from backend.models import Motorista, Usuario
from backend.database import SessionLocal, engine, Base
import sys
import os

# Adiciona o diretório atual ao path para importar o backend
sys.path.append(os.getcwd())

# Tenta carregar as variáveis de ambiente do arquivo .env (importante para a DATABASE_URL)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def disparar_teste_vibracao(motorista_id=None):
    # Garante que as tabelas existam no banco de dados antes de realizar a consulta
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        if motorista_id is None:
            # Busca o último motorista que possui um token de push válido
            motorista = db.query(Motorista).filter(
                Motorista.push_token.isnot(None)).order_by(Motorista.id.desc()).first()
            if motorista:
                print(
                    f"ℹ️ Selecionado automaticamente: {motorista.nome} (ID: {motorista.id})")
            else:
                print("❌ Erro: Nenhum motorista com push_token encontrado no banco.")
                return
        else:
            motorista = db.query(Motorista).filter(
                Motorista.id == motorista_id).first()

        if not motorista or not motorista.push_token:
            print(
                f"❌ Erro: Motorista ID {motorista_id} não encontrado ou ainda não aceitou notificações no celular.")
            return

        print(f"🚀 Enviando Push de teste para {motorista.nome}...")

        data = {
            "title": "🚨 TESTE DE EMERGÊNCIA",
            "body": "Se o seu celular vibrou, a Central Transfers está operando 100%!",
            # Ritmo de alerta
            "vibrate": [500, 110, 500, 110, 450, 110, 200, 110, 170, 40, 450, 110, 200, 110, 170, 40]
        }

        sucesso = notifier.send_web_push(motorista.push_token, data)

        if sucesso:
            print("✅ Notificação enviada! Verifique o celular do motorista.")
        else:
            print("⚠️ Falha ao entregar. O navegador pode ter invalidado o token.")

    finally:
        db.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        disparar_teste_vibracao(int(sys.argv[1]))
    else:
        print("💡 Dica: Você pode passar o ID do motorista. Tentando encontrar um token automaticamente...")
        disparar_teste_vibracao()
