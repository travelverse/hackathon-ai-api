# -*- coding: utf-8 -*-
import os
import logging
import functools
from typing import Sequence, List, Optional
from pydantic import BaseModel, Field
from loguru import logger
from fastapi import Header
from fastapi.openapi.utils import get_openapi
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
import system


class ServiceSettings(BaseModel, extra="forbid"):
    host: str = "0.0.0.0"
    port: int = 8000
    uds: Optional[str] = None
    fd: Optional[int] = None
    loop: Optional[str] = None
    http: Optional[str] = None
    ws: Optional[str] = None
    ws_max_size: Optional[int] = Field(None, alias="ws-max-size")
    ws_max_queue: Optional[int] = Field(None, alias="ws-max-queue")
    ws_ping_interval: Optional[float] = Field(None, alias="ws-ping-interval")
    ws_ping_timeout: Optional[float] = Field(None, alias="ws-ping-timeout")
    ws_per_message_deflate: Optional[bool] = Field(None, alias="ws-per-message-deflate")
    lifespan: Optional[str] = None
    interface: Optional[str] = None
    reload: Optional[bool] = None
    reload_dir: Optional[List[str]] = Field(None, alias="reload-dir")
    reload_include: Optional[List[str]] = Field(None, alias="reload-include")
    reload_exclude: Optional[List[str]] = Field(None, alias="reload-exclude")
    reload_delay: Optional[float] = Field(None, alias="reload-delay")
    workers: Optional[int] = None
    env_file: Optional[str] = Field(None, alias="env-file")
    log_config: Optional[str] = Field(None, alias="log-config")
    log_level: Optional[str] = Field(None, alias="log-level")
    access_log: Optional[bool] = Field(None, alias="access-log")
    proxy_headers: Optional[bool] = Field(None, alias="proxy-headers")
    server_header: Optional[bool] = Field(None, alias="server-header")
    date_header: Optional[bool] = Field(None, alias="date-header")
    forwarded_allow_ips: Optional[str] = Field(None, alias="forwarded-allow-ips")
    root_path: Optional[str] = Field(None, alias="root-path")
    limit_concurrency: Optional[int] = Field(None, alias="limit-concurrency")
    backlog: Optional[int] = None
    limit_max_requests: Optional[int] = Field(None, alias="limit-max-requests")
    timeout_keep_alive: Optional[int] = Field(None, alias="timeout-keep-alive")
    timeout_graceful_shutdown: Optional[int] = Field(None, alias="timeout-graceful-shutdown")
    ssl_keyfile: Optional[str] = Field(None, alias="ssl-keyfile")
    ssl_certfile: Optional[str] = Field(None, alias="ssl-certfile")
    ssl_keyfile_password: Optional[str] = Field(None, alias="ssl-keyfile-password")
    ssl_version: Optional[int] = Field(None, alias="ssl-version")
    ssl_cert_reqs: Optional[int] = Field(None, alias="ssl-cert-reqs")
    ssl_ca_certs: Optional[str] = Field(None, alias="ssl-ca-certs")
    ssl_ciphers: Optional[str] = Field(None, alias="ssl-ciphers")
    header: Optional[str] = None
    use_colors: Optional[bool] = Field(None, alias="use-colors")
    app_dir: Optional[str] = Field(None, alias="app-dir")
    h11_max_incomplete_event_size: Optional[int] = Field(None, alias="h11-max-incomplete-event-size")
    debug: Optional[bool] = False


class CORSSettings(BaseModel, extra="allow"):
    active: bool = False
    allow_origins: Sequence[str] = Field([], alias="allow-origins")
    allow_methods: Sequence[str] = Field(["GET"], alias="allow-methods")
    allow_headers: Sequence[str] = Field([], alias="allow-headers")
    allow_credentials: bool = Field(False, alias="allow-credentials")
    allow_origin_regex: str = Field(None, alias="allow-origin-regex")
    expose_headers: Sequence[str] = Field([], alias="expose-headers")
    max_age: int = Field(600, alias="max-age")


class InterceptHandler(logging.Handler):
    """ loguru intercept """
    def emit(self, record: logging.LogRecord):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging():
    """Setup uvicorn logger to use loguru."""
    loggers = [
        # pylint: disable=E1101
        logging.getLogger(name) for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn.")
    ]
    for instance in loggers:
        instance.handlers = []

    logging.getLogger("uvicorn").handlers = [InterceptHandler()]


def setup_options(app, debug=False):
    """Setup options for app and all sub-apps.

    :param app: FastAPI app.
    :param debug: enable debug mode.
    """
    for route in app.routes:
        if hasattr(route.app, "debug"):
            route.app.debug = debug
            setup_options(route, debug)


def openapi(app, description):
    """ openapi callback """
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title or system.project.name,
        version=app.version or system.project.version,
        openapi_version=app.openapi_version,
        description=app.description or description,
        terms_of_service=app.terms_of_service,
        contact=app.contact, license_info=app.license_info,
        routes=app.routes, tags=app.openapi_tags, servers=app.servers
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "/static/images/vendor-logo.png"
    }
    if hasattr(app, "security") and app.security.active:
        security_schemes = {
            "APIKeyHeader": {"type": "apiKey", "in": "header", "name": app.security.header}
        }
        openapi_schema.setdefault(
            "components", {}).setdefault("securitySchemes", {}).update(security_schemes)
        openapi_schema.setdefault("security", []).append({"APIKeyHeader": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema


def setup_openapi(apps):
    """Setup openapi metadata for ReDoc and Swagger.

    :param apps: list of FastAPI apps.
    """
    get_redoc_html.__kwdefaults__["redoc_favicon_url"] = "/favicon.ico"  # noqa
    get_swagger_ui_html.__kwdefaults__["swagger_favicon_url"] = "/favicon.ico"  # noqa

    description = None
    if os.path.isfile(os.path.join(system.environment.root, "docs", "description.md")):
        with open(os.path.join(system.environment.root, "docs", "description.md"), "r", encoding="utf-8") as handle:
            description = handle.read()

    for app in apps:
        app.openapi = functools.partial(openapi, app, description)


def headers(
        metadata: Optional[str] = Header(
            None, alias="X-Request-Metadata", title="X-Request-Metadata",
            example="""{"jobid": "50554d6e-29bb-11e5-b345-feff819cdc9f"}""",
            description="""Properties in dict-like {"key": "value"} format"""
        )
):
    """Common headers setup."""
    return metadata


def responses(*args: List[int]):
    """Common responses definitions."""
    definitions = {
        403: {"description": "Forbidden", "content": {"application/json": {
              "schema": {
                  "title": "Message", "required": ["message"], "type": "object",
                  "properties": {"detail": {"title": "Detail", "type": "string"}}
              }, "example": {"detail": "Unauthorized"}}}},
        404: {"description": "Not Found", "content": {"application/json": {
              "schema": {
                  "title": "Message", "required": ["message"], "type": "object",
                  "properties": {"detail": {"title": "Detail", "type": "string"}}
              }, "example": {"detail": "Item not found"}}}},
        500: {"description": "Internal Server Error", "content": {"text/plain": {
              "schema": {"type": "string"}, "example": "Internal Server Error"}}}
    }
    return {code: definitions[code] for code in args}
