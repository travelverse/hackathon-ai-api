# -*- coding: utf-8 -*-
# pylint: disable=W0707,C0207,R0401
import re
import asyncio
from functools import wraps
import sqlmodel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import exc
from sqlalchemy.ext.asyncio import create_async_engine
from modules.database.settings import AlchemySettings
from modules.database.module import DatabaseException

# just aliases for convenience
session, async_session = sqlmodel.Session, AsyncSession

compatibility = {
    "sqlite": {
        "pysqlite": "sync", "aiosqlite": "async"
    },
    "postgresql": {
        "psycopg2": "sync", "pg8000": "sync", "asyncpg": "async",
        "psycopg2cffi": "sync"
    },
    # "mysql": {
    #     "mysqldb": "sync", "pymysql": "sync", "asyncmy": "async",
    #     "aiomysql": "async", "pyodbc": "sync"
    # },
    # "mariadb": {
    #     "mysqldb": "sync", "pymysql": "sync", "asyncmy": "async",
    #     "aiomysql": "async", "pyodbc": "sync"
    # },
    # "oracle": {
    #     "cx_oracle": "sync"
    # },
    # "mssql": {
    #     "pymssql": "sync", "pyodbc": "sync"
    # }
}


def create_engine(dialect: str, driver: str, settings: dict):
    """Create database engine.

    :param dialect: database dialect.
    :param driver: database driver.
    :param settings: database settings.
    """
    settings = AlchemySettings(**settings)
    if compatibility[dialect][driver] == "sync":
        return sqlmodel.create_engine(**settings.dict(exclude={"migrations"}, exclude_defaults=True))
    return create_async_engine(**settings.dict(exclude={"migrations"}, exclude_defaults=True))


def sqlmodel_exceptions(function: callable):
    """Exceptions handling decorator."""
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except exc.SQLAlchemyError as ex:
            raise DatabaseException(re.sub(r"[\"()]", "", str(ex).split("\n")[0].replace(") (", ": ")), ex)
        except ConnectionRefusedError as ex:  # special case for some new drivers
            raise DatabaseException("Connection refused", ex)

    @wraps(function)
    async def wrapper_async(*args, **kwargs):
        try:
            return await function(*args, **kwargs)
        except exc.SQLAlchemyError as ex:
            raise DatabaseException(re.sub(r"[\"()]", "", str(ex).split("\n")[0].replace(") (", ": ")), ex)
        except ConnectionRefusedError as ex:  # special case for some new drivers
            raise DatabaseException("Connection refused", ex)

    if asyncio.iscoroutinefunction(function):
        return wrapper_async
    return wrapper
