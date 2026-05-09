import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool, create_engine
from alembic import context

# 1. Garante que o Python encontre a pasta 'backend' na raiz do projeto
sys.path.append(os.getcwd())

# 2. Importa as suas configurações e os seus modelos
from backend.config import settings
from backend.database import Base
from backend import models  # Essencial para o 'autogenerate' detectar as tabelas

# Este é o objeto de configuração do Alembic, que dá acesso aos valores do arquivo .ini
config = context.config

# Interpreta o arquivo de configuração para o sistema de log
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

    # 3. Define o metadata para o modo 'autogenerate'
    target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline'."""
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Executa migrações no modo 'online'."""

    # 4. Usa a URL tratada do seu config.py (resolve o problema do postgres:// e do :port)
    connectable = create_engine(
        settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()