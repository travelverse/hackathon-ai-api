# -*- coding: utf-8 -*-
from typing import List, Optional
import typer
import system
import modules.database.module as database


@system.runtime.cli.command(
    name="database:migrate", options_metavar="[options]",
    context_settings={"ignore_unknown_options": True}
)
def migrate(
    alias: str = typer.Argument(..., metavar="alias", help="Database alias."),
    args: Optional[List[str]] = typer.Argument(None, metavar="args", help="Migrator arguments")
):
    """Run database migrations."""
    database.migrate(f"runner.sh database:migrate {alias}", alias, args)


@system.runtime.cli.command(
    name="database:seed", options_metavar="[options]", no_args_is_help=True
)
def seed(
    alias: str = typer.Argument(..., metavar="alias", help="Database alias."),
    name: str = typer.Argument(None, metavar="name", help="Seed name.")
):
    """Run database seeding."""
    database.seed(alias, name)
