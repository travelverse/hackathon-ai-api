# -*- coding: utf-8 -*-
# pylint: disable=E1101
import asyncio
import fnmatch
import importlib
from logging.config import fileConfig
from loguru import logger
from alembic import context
from sqlmodel import SQLModel
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine
from modules.database.sqlmodel import compatibility


config = context.config
fileConfig(config.file_config)
version_table = config.get_main_option("migrations")

# this is needed to reveal models for autogenerate
for module in config.get_section_option("autogenerate", "modules").split(","):
    try:
        __import__(module)
    except ImportError:
        logger.error(f"Failed to import '{module}' module.")

package, alias = config.get_main_option("blacklist").rsplit(".", 1)
try:
    blacklist = getattr(importlib.import_module(package), alias)
except (ImportError, AttributeError):
    blacklist = {}

target_metadata = SQLModel.metadata


def include_name(name, kind, *_):
    """Skip blacklisted tables."""
    if kind == "table" and "tables" in blacklist:
        if any(fnmatch.fnmatch(name, table) for table in blacklist["tables"]):
            return False
    return True


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table=version_table,
        include_schemas=True,
        include_name=include_name
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table=version_table,
            include_schemas=True,
            include_name=include_name
        )

        with context.begin_transaction():
            context.run_migrations()


def do_run_migrations(connection):
    """Run migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table=version_table,
        include_schemas=True,
        include_name=include_name
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online_async():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    dialect = config.get_main_option("dialect")
    driver = config.get_main_option("driver")
    if compatibility[dialect][driver] == "sync":
        run_migrations_online()
    else:
        asyncio.run(run_migrations_online_async())
