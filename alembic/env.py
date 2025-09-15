import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from logging.config import fileConfig
from urllib.parse import urlparse, urlunparse
from alembic import context
from sqlalchemy import create_engine, pool
from app.core.config import settings
from app.core.db import Base
from app.query_service.models import Request

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def get_sync_url():
    parsed = urlparse(settings.DB_URL)
    if "+asyncpg" not in parsed.scheme:
        raise ValueError("DB_URL must use asyncpg driver")
    return urlunparse(parsed._replace(scheme=parsed.scheme.replace("+asyncpg", "+psycopg2")))


target_metadata = Base.metadata


def run_migrations_offline():
    context.configure(
        url=get_sync_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    sync_engine = create_engine(
        get_sync_url(),
        poolclass=pool.NullPool,
    )
    with sync_engine.connect() as connection:
        do_run_migrations(connection)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
