# -*- coding: utf-8 -*-
import os
import sys
import time
import logging
import warnings
import importlib
import subprocess
from glob import glob
from contextvars import ContextVar
from typing import List, Dict, Any
from pkg_resources import working_set  # noqa
from dotenv import load_dotenv
import tomlkit
from loguru import logger
import typer
from settings import Locations, Settings
from pydantic import BaseModel, ValidationError


def require_packages(packages: List[str]):
    """Suggest and install packages.

    :param packages: list of packages.
    """
    names = {package.split("==")[0] for package in packages}
    mapping = {package.split("==")[0]: package for package in packages}
    if names.issubset(environment.packages):
        return
    missing = {mapping[name] for name in names.difference(environment.packages)}
    typer.echo(
        typer.style(f"Following packages are required but missing: {', '.join(missing)}", fg=typer.colors.YELLOW))
    response = typer.prompt(typer.style("Install them now [y/n] ?", fg=typer.colors.YELLOW))
    if response.lower() == "y":
        process = subprocess.run(["poetry", "add", *missing], universal_newlines=True, check=False)
        if process.returncode == 0:
            typer.echo(typer.style("Everything looks good, restart application", fg=typer.colors.GREEN))
            sys.exit(0)
        else:
            typer.echo(typer.style("Installation failed, check output", fg=typer.colors.RED))
            sys.exit(0)
    else:
        typer.echo(typer.style("They are really required, so install them first", fg=typer.colors.RED))


class Environment(BaseModel):
    mode: str
    root: str
    environ: dict
    packages: list


class Runtime(BaseModel, extra="allow"):
    pass


class Project(BaseModel):
    name: str
    version: str
    description: str
    authors: List[Dict[str, str]]
    dependencies: List[str]


load_dotenv()
time.tzset()
try:
    environment = Environment(
        mode=os.getenv("APP_MODE"),
        root=os.getenv("APP_ROOT"),
        environ=os.environ,
        packages={pkg.key for pkg in list(working_set)}
    )
    path = Locations()
    for key, value in path.dict().items():
        setattr(path, key, getattr(path, key).replace("{root}", environment.root))

    runtime = Runtime()
    context = ContextVar("app")
    with open(os.path.join(environment.root, "pyproject.toml"), "r", encoding="utf-8") as handle:
        project = Project.parse_obj(tomlkit.load(handle)["project"])
    with open(os.path.join(environment.root, "config/settings.toml"), "r", encoding="utf-8") as handle:
        settings = Settings.parse_obj(tomlkit.load(handle).unwrap())

    logger.remove()
    logger.add(sys.stdout, colorize=True,
               level=settings.logging.level,
               format=settings.logging.format)

    if environment.environ.get("APP_DEPRECATIONS") == "false":
        logging.captureWarnings(True)
        warnings.filterwarnings("ignore", category=DeprecationWarning)

    for target in sorted(glob(os.path.join(environment.root, "app", "modules", "*", "module.py"))):
        module = importlib.import_module(f"modules.{target.split(os.path.sep)[-2]}.module")
        if getattr(module, "enabled", False) and hasattr(module, "bootstrap"):
            if not getattr(module, "bootstrap")():
                logger.error("Failed to initialize application, startup aborted")
                sys.exit(1)

except ValidationError as ex:
    logger.error(ex)
    sys.exit(1)
