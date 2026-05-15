import logging
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. Importe o Base e os Models do seu projeto
from backend.database import Base
from backend import models
from backend.config import settings

# interpreta o arquivo de config do alembic
config = context.config

# Configura o logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 2. Configure o target_metadata para o autogenerate funcionar
target_metadata = Base.metadata


def get_url():
    return settings.DATABASE_URL.replace("postgres://", "postgresql://")


def run_migrations_offline() -> None:
    """Executa migrações no modo 'offline'."""
    url = get_url()
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
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()

    connect_args = {}
    if get_url().startswith("sqlite"):
        connect_args = {"check_same_thread": False}

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        connect_args=connect_args
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True  # Essencial para SQLite
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
