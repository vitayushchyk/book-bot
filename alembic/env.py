import asyncio
import logging
from logging.config import fileConfig

from alembic import context
from bot.core.config import settings
from bot.db.book_db import *  # noqa*
from bot.db.conection import engine

config = context.config
if config.config_file_name:
    fileConfig(config.config_file_name)
config.set_main_option(name="sqlalchemy.url", value=str(settings.db_connection_uri))
target_metadata = SQLModel.metadata


logging.info(f"Database connection URI: {settings.db_connection_uri}")


def run_migrations_offline() -> None:
    url = settings.db_connection_uri
    logging.info(f"Running migrations in offline mode with URL: {url}")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    logging.info("Running migrations in online mode with an active connection.")
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    logging.info("Attempting to connect to database...")
    async with engine.connect() as connection:
        logging.info("Database connection established successfully.")
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
