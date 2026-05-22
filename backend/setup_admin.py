import logging
from backend.database import SessionLocal
from backend.models import Usuario
from backend.auth import hash_senha
from backend.config import settings

logger = logging.getLogger(__name__)


def criar_admin_mestre():
    """
    Garante a existência de um administrador mestre no banco de dados.
    Lógica executada no startup da aplicação (lifespan).
    """
    db = SessionLocal()
    try:
        # Busca credenciais das configurações (carregadas via .env ou defaults)
        email_admin = getattr(settings, 'ADMIN_EMAIL',
                              "admin@centraltransfers.com")
        senha_admin = getattr(settings, 'ADMIN_PASS', "Mudar123")

        # Verifica se já existe um administrador
        existe = db.query(Usuario).filter(Usuario.role == "admin").first()

        if not existe:
            logger.info(
                f"🚀 Primeiro deploy detectado. Criando Admin: {email_admin}")
            admin = Usuario(
                email=email_admin,
                senha_hash=hash_senha(senha_admin),
                role="admin"
            )
            db.add(admin)
            db.commit()
            logger.info(f"✅ Administrador mestre criado com sucesso. Email: {email_admin}. "
                        "Por favor, altere a senha padrão após o primeiro login.")
        else:
            logger.info("ℹ️ Administrador mestre já configurado.")
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar Admin Mestre: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    # Configuração básica de logging para quando rodar via CLI
    logging.basicConfig(level=logging.INFO)
    criar_admin_mestre()
