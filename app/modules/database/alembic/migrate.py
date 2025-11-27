# -*- coding: utf-8 -*-
import os
from loguru import logger
import alembic.config
from modules.database.settings import AlchemySettings
import system


def execute(prog: str, args: list, dialect: str, driver: str, settings: dict,
            schemas: str, models: str, blacklist: str, migrations: str = None):
    """Bootstrap and run Alembic.

    :param prog: cli prog name.
    :param args: alembic arguments.
    :param dialect: database dialect.
    :param driver: database driver.
    :param settings: database settings.
    :param schemas: migration schemas location.
    :param models: model modules for autogenerate.
    :param blacklist: blacklist module.
    :param migrations: override version table name.
    """
    if not args:
        args = ["-h"]

    if "--autogenerate" in args and not system.environment.mode == "development":
        logger.warning("this command intended to use in development environment")
        return

    settings = AlchemySettings(**settings)
    cli = alembic.config.CommandLine(prog=prog)
    options = cli.parser.parse_args(args)
    if not hasattr(options, "cmd"):
        cli.parser.print_help()
        return

    config = alembic.config.Config(cmd_opts=options)
    config.set_main_option("script_location", os.path.join(os.path.dirname(__file__)))
    config.set_main_option("file_template", "%%(rev)s_%%(slug)s")
    config.set_main_option("truncate_slug_length", "40")
    config.set_main_option("revision_environment", "false")
    config.set_main_option("sourceless", "false")
    config.set_main_option("version_locations", schemas)
    config.set_main_option("blacklist", blacklist)
    config.set_main_option("output_encoding", "utf-8")
    config.set_main_option("migrations", migrations or "migrations")
    config.set_main_option("dialect", dialect)
    config.set_main_option("driver", driver)
    config.set_main_option("sqlalchemy.url", settings.url)
    config.set_section_option("autogenerate", "modules", models)
    config.file_config.add_section("post_write_hooks")  # pylint: disable=E1101
    config.set_section_option("post_write_hooks", "hooks", "black")
    config.set_section_option("post_write_hooks", "black.type", "console_scripts")
    config.set_section_option("post_write_hooks", "black.entrypoint", "black")
    config.set_section_option("post_write_hooks", "black.options", "-l 120 -q")
    # logging configuration
    config.set_section_option("loggers", "keys", "root,sqlalchemy,alembic")
    config.set_section_option("handlers", "keys", "console")
    config.set_section_option("formatters", "keys", "generic")
    config.set_section_option("logger_root", "level", "WARN")
    config.set_section_option("logger_root", "handlers", "console")
    config.set_section_option("logger_root", "qualname", "")
    config.set_section_option("logger_sqlalchemy", "level", "WARN")
    config.set_section_option("logger_sqlalchemy", "handlers", "")
    config.set_section_option("logger_sqlalchemy", "qualname", "sqlalchemy.engine")
    config.set_section_option("logger_alembic", "level", "INFO")
    config.set_section_option("logger_alembic", "handlers", "")
    config.set_section_option("logger_alembic", "qualname", "alembic")
    config.set_section_option("handler_console", "class", "modules.database.logging.InterceptHandler")
    config.set_section_option("formatter_generic", "pass", "pass")

    cli.run_cmd(config, options)
