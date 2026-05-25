import os
import subprocess
import sys
from pathlib import Path


# Carrega variáveis de ambiente se o pacote estiver disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Verificação de versão mínima
if sys.version_info < (3, 10):
    print("❌ Este sistema requer Python 3.10 ou superior.")
    sys.exit(1)

# Garante que o diretório raiz está no path para importar o backend
sys.path.append(os.getcwd())


def run_step(command, description):
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Falha em: {description}")
        return False


def update_env_variable(key, value):
    """Atualiza ou adiciona uma variável no arquivo .env"""
    env_path = Path(".env")
    if not env_path.exists():
        return False

    lines = env_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    found = False

    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


def main():
    print("🏗️  PREPARANDO LANÇAMENTO CENTRAL TRANSFERS")
    print("=" * 45)

    # Nota: A verificação de variáveis críticas agora é feita de forma inteligente
    # pelo backend.check_standards (Step 1), que permite a correção imediata.

    # 1. Auditoria de Segurança e Configurações
    try:
        import check_standards as audit
    except ImportError:
        import backend.check_standards as audit
    success, missing_keys = audit.run_audit()

    if not success:
        print("\n🛠️  Detectamos pendências na configuração.")
        for key in missing_keys:
            if "VAPID" in key:
                continue  # Tratado abaixo automaticamente
            print(f"\n⚠️  A variável {key} está ausente ou inválida.")
            val = input(f"👉 Cole aqui o VALOR para {key}: ").strip()
            if val:
                update_env_variable(key, val)

        # Automação de Chaves VAPID se estiverem faltando
        if any("VAPID" in k for k in missing_keys):
            print("\n🔑 Gerando chaves VAPID para Notificações Push...")
            try:
                import gerar_chaves
                # O script gerar_chaves.py já tem a lógica, mas vamos integrar aqui
                from cryptography.hazmat.primitives.asymmetric import ec
                import base64
                pk = ec.generate_private_key(ec.SECP256R1())
                private_b64 = base64.urlsafe_b64encode(pk.private_numbers(
                ).private_value.to_bytes(32, 'big')).decode('utf-8').strip("=")
                public_b64 = base64.urlsafe_b64encode(pk.public_key().public_bytes(
                    encoding=getattr(__import__(
                        'cryptography.hazmat.primitives.serialization').hazmat.primitives.serialization, 'Encoding').X962,
                    format=getattr(__import__('cryptography.hazmat.primitives.serialization')
                                   .hazmat.primitives.serialization, 'PublicFormat').UncompressedPoint
                )).decode('utf-8').strip("=")

                update_env_variable("VAPID_PRIVATE_KEY", private_b64)
                update_env_variable("VAPID_PUBLIC_KEY", public_b64)
                print(f"✅ Chaves VAPID geradas: PUB({public_b64[:10]}...)")
            except ImportError:
                print("⚠️  Instale 'pywebpush' para gerar chaves automaticamente.")

        sys.exit(0)

    # 1.1 Verificação de Conectividade e Integridade
    print("\n🔍 Testando conexão com o Banco de Dados...")

    # 2. Migrações de Banco de Dados (aplicamos antes da checagem de integridade)
    alembic_cmd = "alembic upgrade head"
    # Se o alembic.ini estiver dentro da pasta backend, usamos o sinalizador -c
    if os.path.exists("backend/alembic.ini"):
        alembic_cmd = "alembic -c backend/alembic.ini upgrade head"
    elif not os.path.exists("alembic.ini"):
        print("⚠️  Aviso: alembic.ini não encontrado na raiz.")
        if os.path.exists("backend/alembic"):
            print(
                "💡 Dica: Verifique se o arquivo alembic.ini foi movido para dentro de 'backend/'.")

    if not run_step(alembic_cmd, "Atualizando esquema do Banco de Dados (Alembic)"):
        print("\n❌ Erro ao aplicar migrações no Banco de Dados.")
        print("DICA: Verifique se o usuário/senha no DATABASE_URL estão corretos.")
        retry = input("Deseja atualizar a DATABASE_URL agora? (s/N): ").lower()
        if retry == 's':
            new_url = input("👉 Cole a nova DATABASE_URL: ").strip()
            if new_url:
                update_env_variable("DATABASE_URL", new_url)
                print("✅ URL atualizada. Execute o script novamente para validar.")
                sys.exit(0)
        else:
            sys.exit(1)

    # 3. Verificação de Conectividade e Integridade (após migrações)
    if not run_step(f"{sys.executable} check_system.py", "Verificando integridade do sistema"):
        print("❌ O sistema não está íntegro para registros reais.")
        sys.exit(1)
    # 4. Setup do Admin Mestre
    # Garantir que o subprocess tenha PYTHONPATH apontando para o diretório do projeto
import os
import sys
import logging
from backend.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("PreFlight")


def run_audit():
    """Valida se o ambiente de produção está configurado corretamente."""
    print("\n✈️  Iniciando Auditoria Pré-Voo (Go-Live)...")
    errors = 0
    failed_keys = []

    # Chaves obrigatórias para o funcionamento básico
    checks = {
        "MERCADO_PAGO_ACCESS_TOKEN": getattr(settings, 'MERCADO_PAGO_ACCESS_TOKEN', None),
        "MERCADO_PAGO_WEBHOOK_SECRET": getattr(settings, 'MERCADO_PAGO_WEBHOOK_SECRET', None),
        "DATABASE_URL": getattr(settings, 'DATABASE_URL', os.getenv("DATABASE_URL")),
        "SECRET_KEY": getattr(settings, 'SECRET_KEY', None),
        "FRONTEND_URL": getattr(settings, 'FRONTEND_URL', os.getenv("FRONTEND_URL")),
        "ALLOWED_ORIGINS": getattr(settings, 'ALLOWED_ORIGINS', os.getenv("ALLOWED_ORIGINS")),
        "VAPID_PRIVATE_KEY": getattr(settings, 'VAPID_PRIVATE_KEY', None),
        "VAPID_PUBLIC_KEY": getattr(settings, 'VAPID_PUBLIC_KEY', None),
        "SMTP_USER": getattr(settings, 'SMTP_USER', os.getenv("SMTP_USER")),
        "SMTP_PASS": getattr(settings, 'SMTP_PASS', os.getenv("SMTP_PASS")),
        "ADMIN_EMAIL": getattr(settings, 'ADMIN_EMAIL', None),
        "ADMIN_PASS": getattr(settings, 'ADMIN_PASS', None),
    }

    for key, value in checks.items():
        if not value or any(x in str(value).lower() for x in ["cole_seu", "seu_segredo", "temporaria", "placeholder"]):
            print(f"❌ ERRO: {key} não configurado corretamente no .env")
            errors += 1
            failed_keys.append(key)
        
        # Validação de HTTPS para Produção
        if key == "FRONTEND_URL" and value and "https://" not in str(value).lower() and "localhost" not in str(value):
            print(f"❌ ERRO: {key} deve usar HTTPS para funcionamento do PWA/Service Worker!")
            errors += 1
            failed_keys.append(key)
        else:
            print(f"✅ {key}: OK")

    # 2. Verificações Opcionais / Informativas (Fora do loop principal)
    whatsapp_token = getattr(settings, 'WHATSAPP_TOKEN', None)
    if not whatsapp_token:
        print("ℹ️  INFO: WhatsApp (Meta) não configurado. O sistema usará apenas WebSockets/WebPush.")
    else:
        print("✅ WHATSAPP: OK")

    sentry = getattr(settings, 'SENTRY_DSN', None)
    if not sentry:
        print("⚠️ AVISO: SENTRY_DSN não configurado. Monitoramento de logs desativado.")

    validation_mode = getattr(settings, 'VALIDATION_MODE', False)
    if validation_mode:
        print("⚠️ AVISO: VALIDATION_MODE está ativo. Desative para Produção!")
        errors += 1

    if errors > 0:
        print(
            f"\n🛑 Auditoria falhou com {errors} erros. O lançamento não é seguro.")
        return False, failed_keys

    print("\n🚀 TUDO PRONTO PARA O GO-LIVE! O sistema está estável.")
    return True, []


if __name__ == "__main__":
    run_audit()
import os
import subprocess
import sys
from pathlib import Path


# Carrega variáveis de ambiente se o pacote estiver disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Verificação de versão mínima
if sys.version_info < (3, 10):
    print("❌ Este sistema requer Python 3.10 ou superior.")
    sys.exit(1)

# Garante que o diretório raiz está no path para importar o backend
sys.path.append(os.getcwd())


def run_step(command, description):
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        print(f"❌ Falha em: {description}")
        return False


def update_env_variable(key, value):
    """Atualiza ou adiciona uma variável no arquivo .env"""
    env_path = Path(".env")
    if not env_path.exists():
        return False

    lines = env_path.read_text(encoding="utf-8").splitlines()
    new_lines = []
    found = False

    for line in lines:
        if line.startswith(f"{key}="):
            new_lines.append(f"{key}={value}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
    return True


def main():
    print("🏗️  PREPARANDO LANÇAMENTO CENTRAL TRANSFERS")
    print("=" * 45)

    # Nota: A verificação de variáveis críticas agora é feita de forma inteligente
    # pelo backend.check_standards (Step 1), que permite a correção imediata.

    # 1. Auditoria de Segurança e Configurações
    try:
        import check_standards as audit
    except ImportError:
        import backend.check_standards as audit
    success, missing_keys = audit.run_audit()

    if not success:
        print("\n🛠️  Detectamos pendências na configuração.")
        for key in missing_keys:
            if "VAPID" in key:
                continue # Tratado abaixo automaticamente
            print(f"\n⚠️  A variável {key} está ausente ou inválida.")
            val = input(f"👉 Cole aqui o VALOR para {key}: ").strip()
            if val:
                update_env_variable(key, val)

        # Automação de Chaves VAPID se estiverem faltando
        if any("VAPID" in k for k in missing_keys):
            print("\n🔑 Gerando chaves VAPID para Notificações Push...")
            try:
                import gerar_chaves
                # O script gerar_chaves.py já tem a lógica, mas vamos integrar aqui
                from cryptography.hazmat.primitives.asymmetric import ec
                import base64
                pk = ec.generate_private_key(ec.SECP256R1())
                private_b64 = base64.urlsafe_b64encode(pk.private_numbers().private_value.to_bytes(32, 'big')).decode('utf-8').strip("=")
                public_b64 = base64.urlsafe_b64encode(pk.public_key().public_bytes(
                    encoding=getattr(__import__('cryptography.hazmat.primitives.serialization').hazmat.primitives.serialization, 'Encoding').X962,
                    format=getattr(__import__('cryptography.hazmat.primitives.serialization').hazmat.primitives.serialization, 'PublicFormat').UncompressedPoint
                )).decode('utf-8').strip("=")
                
                update_env_variable("VAPID_PRIVATE_KEY", private_b64)
                update_env_variable("VAPID_PUBLIC_KEY", public_b64)
                print(f"✅ Chaves VAPID geradas: PUB({public_b64[:10]}...)")
            except ImportError:
                print("⚠️  Instale 'pywebpush' para gerar chaves automaticamente.")

        sys.exit(0)

    # 1.1 Verificação de Conectividade e Integridade
    print("\n🔍 Testando conexão com o Banco de Dados...")

    # 2. Migrações de Banco de Dados (aplicamos antes da checagem de integridade)
    alembic_cmd = "alembic upgrade head"
    # Se o alembic.ini estiver dentro da pasta backend, usamos o sinalizador -c
    if os.path.exists("backend/alembic.ini"):
        alembic_cmd = "alembic -c backend/alembic.ini upgrade head"
    elif not os.path.exists("alembic.ini"):
        print("⚠️  Aviso: alembic.ini não encontrado na raiz.")
        if os.path.exists("backend/alembic"):
            print(
                "💡 Dica: Verifique se o arquivo alembic.ini foi movido para dentro de 'backend/'.")

    if not run_step(alembic_cmd, "Atualizando esquema do Banco de Dados (Alembic)"):
        print("\n❌ Erro ao aplicar migrações no Banco de Dados.")
        print("DICA: Verifique se o usuário/senha no DATABASE_URL estão corretos.")
        retry = input("Deseja atualizar a DATABASE_URL agora? (s/N): ").lower()
        if retry == 's':
            new_url = input("👉 Cole a nova DATABASE_URL: ").strip()
            if new_url:
                update_env_variable("DATABASE_URL", new_url)
                print("✅ URL atualizada. Execute o script novamente para validar.")
                sys.exit(0)
        else:
            sys.exit(1)

    # 3. Verificação de Conectividade e Integridade (após migrações)
    if not run_step(f"{sys.executable} check_system.py", "Verificando integridade do sistema"):
        print("❌ O sistema não está íntegro para registros reais.")
        sys.exit(1)
    # 4. Setup do Admin Mestre
    # Garantir que o subprocess tenha PYTHONPATH apontando para o diretório do projeto
    os.environ.setdefault("PYTHONPATH", os.getcwd())
    if not run_step(f"{sys.executable} setup_admin.py", "Configurando Administrador Mestre"):
        sys.exit(1)

    # 5. Build do Frontend (Automação da Distribuição)
    confirm_build = input(
        "\n📦 Deseja gerar o build de produção do Painel SaaS? (s/N): ")
    if confirm_build.lower() == 's':
        if os.path.exists("painel-saas"):
            # Etapa de Finalização PWA para garantir 100% de prontidão
            print("\n🛠️  Otimizando ativos PWA para instalação...")
            run_step(f"{sys.executable} pwa_finalize.py",
                     "Configurando Manifest, Ícones e Componentes PWA")

            run_step("npm run build --prefix painel-saas",
                     "Gerando build de produção (Vite/PWA)")

            # Automação de auditoria de prontidão
            print("\n🧐 Verificando Score final do PWA...")
            run_step(f"{sys.executable} pwa_status_audit.py",
                     "Auditoria de Percentual PWA")

            # Automação de validação PWA
            run_step(f"{sys.executable} pwa_preflight.py",
                     "Validando integridade dos ativos PWA")

    # 6. Seed opcional
    confirm = input(
        "\n🌱 Deseja popular o banco com dados iniciais (Seed)? (s/N): ")
    if confirm.lower() == 's':
        run_step(f"{sys.executable} seed_db.py", "Populando dados iniciais")

    print("\n" + "═" * 45)
    print("🚀 PROJETO PRONTO PARA PRODUÇÃO!")
    print("1. Sync Railway: 'railway variables --set VAPID_PRIVATE_KEY=...'")
    print("2. Sync Vercel: Adicione VITE_VAPID_PUBLIC_KEY no painel Vercel.")
    print(f"3. Teste Final: python check_production.py {os.getenv('BACKEND_URL', 'SUA_URL_RAILWAY')}")
    print("═" * 45)


if __name__ == "__main__":
    main()
    os.environ.setdefault("PYTHONPATH", os.getcwd())
    if not run_step(f"{sys.executable} setup_admin.py", "Configurando Administrador Mestre"):
        sys.exit(1)

    # 5. Build do Frontend (Automação da Distribuição)
    confirm_build = input(
        "\n📦 Deseja gerar o build de produção do Painel SaaS? (s/N): ")
    if confirm_build.lower() == 's':
        if os.path.exists("painel-saas"):
            # Etapa de Finalização PWA para garantir 100% de prontidão
            print("\n🛠️  Otimizando ativos PWA para instalação...")
            run_step(f"{sys.executable} pwa_finalize.py",
                     "Configurando Manifest, Ícones e Componentes PWA")

            run_step("npm run build --prefix painel-saas",
                     "Gerando build de produção (Vite/PWA)")

            # Automação de auditoria de prontidão
            print("\n🧐 Verificando Score final do PWA...")
            run_step(f"{sys.executable} pwa_status_audit.py",
                     "Auditoria de Percentual PWA")

            # Automação de validação PWA
            run_step(f"{sys.executable} pwa_preflight.py",
                     "Validando integridade dos ativos PWA")

    # 6. Seed opcional
    confirm = input(
        "\n🌱 Deseja popular o banco com dados iniciais (Seed)? (s/N): ")
    if confirm.lower() == 's':
        run_step(f"{sys.executable} seed_db.py", "Populando dados iniciais")

    print("\n" + "═" * 45)
    print("🚀 PROJETO PRONTO PARA PRODUÇÃO!")
    print("1. Sync Railway: 'railway variables --set VAPID_PRIVATE_KEY=...'")
    print("2. Sync Vercel: Adicione VITE_VAPID_PUBLIC_KEY no painel Vercel.")
    print(
        f"3. Teste Final: python check_production.py {os.getenv('BACKEND_URL', 'SUA_URL_RAILWAY')}")
    print("═" * 45)


if __name__ == "__main__":
    main()
