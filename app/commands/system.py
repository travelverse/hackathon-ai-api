# -*- coding: utf-8 -*-
import os
import time
import subprocess
import typer
import system


@system.runtime.cli.command(name="system:freeze", options_metavar="[options]")
def freeze():
    """
    Update conda environment.yml
    """
    result = subprocess.run([
        'conda', 'env', 'export', '--no-builds', '--from-history'], stdout=subprocess.PIPE, check=True)
    lines = result.stdout.decode().split("\n")
    # pylint: disable=W1514
    with open(os.path.join(system.environment.root, "environment.yml"), "w") as handle:
        for line in lines:
            if "name:" in line:
                line = "name: venv"
            if "prefix:" in line or line == "":
                continue
            if "  - conda-forge" not in lines and line == "  - defaults":
                handle.write("  - conda-forge" + "\n")

            handle.write(line + "\n")

    typer.secho("environment.yml successfully updated")


@system.runtime.cli.command(name="system:cleanup", options_metavar="[options]")
def cleanup(
    path: str = typer.Argument(..., metavar="path", help="Path or location."),
    interval: int = typer.Argument(30, metavar="[interval]", help="Older than days interval threshold.")
):
    """
    Cleanup old files.
    """
    skip = [".empty"]
    if hasattr(system.path, path):
        path = getattr(system.path, path)

    current_time = time.time()
    for dirpath, _, filenames in os.walk(path):
        for file in filenames:
            if file in skip:
                continue
            path = os.path.join(dirpath, file)
            creation_time = os.path.getctime(path)
            if (current_time - creation_time) // (24 * 3600) > interval:
                os.unlink(path)
                typer.secho(f"removed {path}")
