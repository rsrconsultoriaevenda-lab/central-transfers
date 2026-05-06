from logging.config import fileConfig
from sqlalchemy import create_engine, pool
from alembic import context

from backend.database import Base
from backend.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

    target_metadata = Base.metadata


def get_database_url():
    # garante compatibilidade com .env e fallback seguro
    return settings.DATABASE_URL


def run_migrations_offline():
    url = get_database_url()

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_engine(
        get_database_url(),
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


            if context.is_offline_mode():
                run_migrations_offline()
            else:
                run_migrations_online()