# -*- coding: utf-8 -*-
import sys
import typer
from loguru import logger
import system
from modules.system.click import setup_click
from modules.system.click import UnsortedGroup


setup_click({
    "styles": {
        "exception": {"fg": "red"},
        "error": {"fg": "red"},
        "usage-prefix": {"fg": "yellow"},
        "heading": {"fg": "yellow"},
        "option-name": {"fg": "blue"},
        "command-name": {"fg": "blue"}
    },
    "max-content-width": 150,
    "column-width": 55,
    "column-spacing": 4
})


if __name__ == "__main__":

    if not system.environment.environ.get("APP_HIDE_BANNER"):
        typer.secho(f":: {system.project.name} v{system.project.version} ::", fg=typer.colors.BLUE)
    try:
        system.runtime.cli = typer.Typer(
            options_metavar="[options]", subcommand_metavar="command [args]...",
            no_args_is_help=True, cls=UnsortedGroup, add_completion=False)
        import commands  # pylint: disable=W0611
        extra = {
            "service-name": system.project.name,
            "service-version": system.project.version
        }
        with logger.contextualize(**extra):
            system.runtime.cli(prog_name="runner.sh", help_option_names=["-h", "--help"])
    except Exception as ex:  # pylint: disable=W0718
        system.logger.exception(ex)
        sys.exit(1)
