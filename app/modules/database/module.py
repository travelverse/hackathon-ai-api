# -*- coding: utf-8 -*-
import os
import asyncio
import importlib
from itertools import chain
from collections import abc
from functools import partial
from urllib.parse import urlparse
from loguru import logger
import typer
import system

enabled = True  # pylint: disable=C0103

registry = {}
# responsibility = {
#     "sqlmodel": ["sqlite", "postgresql", "mysql", "mariadb", "oracle", "mssql"]
# }
responsibility = {
    "sqlmodel": ["postgresql"]
}
packages = {}


class DatabaseException(Exception):
    def __init__(self, message, alchemy):
        super().__init__(message)
        self.alchemy = alchemy


class DatabaseError(DatabaseException):
    pass


class ValidationException(Exception):
    def __init__(self, message, details):
        super().__init__(message)
        self.details = details


class DatabasesDict(abc.MutableMapping, dict):

    def __getitem__(self, key):
        value = dict.__getitem__(self, key)
        if callable(value):
            value = value()
            dict.__setitem__(self, key, value)
        return value

    def __setitem__(self, key, value):
        dict.__setitem__(self, key, value)

    def __delitem__(self, key):
        value = dict.__getitem__(self, key)
        value.dispose()
        dict.__delitem__(self, key)

    def __iter__(self):
        return dict.__iter__(self)

    def __len__(self):
        return dict.__len__(self)


def bootstrap():
    """ system initialization bootstrap """
    result = True
    system.runtime.databases = DatabasesDict()
    if hasattr(system.settings, "database"):
        missed = set()
        for alias in system.settings.database:
            if isinstance(system.settings.database[alias], dict):
                settings = system.settings.database[alias]
                try:
                    connection = urlparse(settings.get("url", ""))
                    dialect, driver, *_ = connection.scheme.split("+")
                except ValueError:
                    logger.error(f"Incorrect or incomplete configuration for {alias}")
                    result = False
                    continue
                try:
                    if dialect in responsibility["sqlmodel"]:
                        from modules.database.sqlmodel import create_engine  # pylint: disable=C0415
                        importlib.import_module(driver)
                        system.runtime.databases[alias] = partial(create_engine, dialect, driver, settings)
                        registry[alias] = {"dialect": dialect, "driver": driver}
                    if dialect not in list(chain(*responsibility.values())):
                        logger.error(f"Unsupported dialect {dialect} for {alias}")
                        result = False
                except KeyError as ex:
                    logger.error(f"Unsupported driver {str(ex)} for {alias}")
                    result = False
                except TypeError as ex:
                    logger.error(f"Type error for {alias}:\n{' '*4}{str(ex)}")
                    result = False
                except ModuleNotFoundError as ex:
                    logger.warning(f"Package '{packages.get(ex.name, ex.name)}' required for {alias} not found")
                    missed.add(packages.get(ex.name, ex.name))
            else:
                logger.error(f"Incorrect configuration for '{alias}' database")
                return False

        if missed:
            system.require_packages(missed)

    return result


def migrate(prog: str, alias: str, args: list, schemas: str = "app/database/schemas",
            models: str = "database.models", blacklist: str = "database.schemas.blacklist",
            migrations: str = "migrations"):
    """Run corresponding migration subsystem.

    :param prog: cli prog name.
    :param alias: database connection alias.
    :param args: migrator arguments.
    :param schemas: migration schemas location.
    :param models: model modules for autogenerate.
    :param blacklist: blacklist module.
    :param migrations: migrations table name.
    """
    if alias in registry:
        settings = system.settings.database[alias]
        if registry[alias]["dialect"] in responsibility["sqlmodel"]:
            from modules.database.alembic.migrate import execute  # pylint: disable=C0415
            execute(prog, args, registry[alias]["dialect"], registry[alias]["driver"],
                    settings, os.path.join(schemas, alias), f"{models}.{alias}",
                    f"{blacklist}.{alias}", migrations)
    else:
        logger.error(f"Alias {alias} is not registered")


def seed(alias: str, name: str = None, seeds: str = "app/database/seeds", modules: str = "database.seeds"):
    """Run seeder.

    :param alias: database connection alias.
    :param name: seed name.
    :param seeds: seeds location.
    :param modules: seeds modules.
    """
    if alias in registry:
        if name is None:
            typer.echo(typer.style("available seeds: ", fg=typer.colors.GREEN))
            for file in os.listdir(f"{seeds}/{alias}"):
                if not file.startswith("__") and file.endswith(".py"):
                    typer.echo(f"  {file[:-3]}")
            return
        try:
            seeder = importlib.import_module(f"{modules}.{alias}.{name}")
            if asyncio.iscoroutinefunction(seeder.seed):
                asyncio.get_event_loop().run_until_complete(
                    seeder.seed(system.runtime.databases[alias]))
            else:
                seeder.seed(system.runtime.databases[alias])
            logger.info("Operation successfully completed")
        except ImportError:
            logger.error("Seed not found.")
        except AttributeError as ex:
            logger.error(str(ex))
    else:
        logger.error(f"Alias {alias} is not registered")
