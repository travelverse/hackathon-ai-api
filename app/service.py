# -*- coding: utf-8 -*-
# pylint: disable=R0801
import sys
import uvicorn
import typer
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import system
from modules.system.click import setup_click
from modules.system.fastapi import setup_logging
from modules.system.fastapi import setup_options, setup_openapi
from modules.system.fastapi import ServiceSettings, CORSSettings
from modules.system.security import SecuritySettings
from modules.system.security import GuardMiddleware
from middlewares import MetadataMiddleware
import handlers

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
setup_logging()


if __name__ == "__main__":

    if not system.environment.environ.get("APP_HIDE_BANNER"):
        typer.secho(f":: {system.project.name} v{system.project.version} ::", fg=typer.colors.BLUE)
    try:
        settings = ServiceSettings(**getattr(system.settings, "service", {}))
        options = settings.dict(exclude_none=True, by_alias=True)
        for option, value in options.items():
            if option in ["debug"]:
                continue
            if f"--{option}" not in sys.argv:
                if isinstance(value, bool):
                    if value:
                        sys.argv.extend([f"--{option}"])
                    continue
                if isinstance(value, list):
                    for item in value:
                        sys.argv.extend([f"--{option}", str(item)])
                    continue
                sys.argv.extend([f"--{option}", str(value)])
        if system.environment.mode == "development":
            if "--reload" not in sys.argv and options.setdefault("reload", True):
                sys.argv.extend(["--reload"])
            if "--reload" in sys.argv:
                sys.argv.extend([
                    "--reload-include", "settings.toml"
                ])
        uvicorn.main()  # pylint: disable = E1120
    except Exception as ex:  # pylint: disable = W0718
        system.logger.exception(ex)
else:
    settings = {}
    registry = {}
    app = FastAPI(
        title=system.project.name,
        version=system.project.version,
        docs_url=None, redoc_url=None, openapi_url=None
    )
    api = FastAPI(
        title=system.project.name,
        version=system.project.version
    )
    api.name = "api"
    api.default = "/redoc"

    app.mount("/api", api, name="api")
    registry.update({"api": api})
    try:
        settings = ServiceSettings(**getattr(system.settings, "service", {}))
        for module in handlers.export:
            if hasattr(module, "router"):
                if not hasattr(module.router, "app"):
                    raise RuntimeError(f"attribute {module.__name__}.router.app is missing")
                if module.router.app == "app":
                    app.include_router(module.router)
                else:
                    if module.router.app not in registry:
                        raise RuntimeError(f"subapp with name {module.router.app} not registered")
                    registry[module.router.app].include_router(module.router)
            if hasattr(module, "subapp"):
                for attr in ["name", "path", "default"]:
                    if not hasattr(module.subapp, attr):
                        raise RuntimeError(f"attribute {module.__name__}.subapp.{attr} is missing")
                if module.subapp.name in registry:
                    raise RuntimeError(f"subapp with name {module.subapp.name} already registered")
                app.mount(module.subapp.path, module.subapp, module.subapp.name)
                registry.update({module.subapp.name: module.subapp})
    except Exception as ex:  # pylint: disable = W0718
        system.logger.exception(ex)
        sys.exit(1)

    setup_options(app, debug=settings.debug)
    setup_openapi(registry.values())
    app.add_middleware(MetadataMiddleware)
    configured = set()
    cors = CORSSettings(**getattr(system.settings, "cors", {}))
    security = SecuritySettings(**getattr(system.settings, "security", {}))
    for name, subapp in registry.items():

        current = getattr(security, name, None)
        if current:
            if "active" in current and current["active"]:
                subapp.security = SecuritySettings(**current)
                subapp.include_router(handlers.security.router)
                subapp.add_middleware(GuardMiddleware, security=subapp.security)
        elif security.active:
            subapp.security = security
            subapp.include_router(handlers.security.router)
            subapp.add_middleware(GuardMiddleware, security=subapp.security)

        if getattr(cors, name, {"active": False})["active"]:
            configured.add("cors")
            params = CORSSettings(**getattr(cors, name)).dict(exclude={"active"})
            subapp.add_middleware(CORSMiddleware, **params)

    if "cors" not in configured and cors.active:
        params = cors.dict(include=CORSSettings.__fields__.keys(), exclude={"active"})
        app.add_middleware(CORSMiddleware, **params)

    app.mount("/static", StaticFiles(directory=system.path.static), name="static")
    system.runtime.templates = Jinja2Templates(directory=system.path.templates)

    try:
        # pylint: disable=E1101
        for module in handlers.export:
            if hasattr(module, "callback") and callable(module.callback):
                module.callback()
    except Exception as ex:  # pylint: disable=W0718
        system.logger.exception(ex)
        sys.exit(1)
