# -*- coding: utf-8 -*-
import ast
from loguru import logger
from starlette.middleware.base import BaseHTTPMiddleware
import system


class MetadataMiddleware(BaseHTTPMiddleware):
    """Metadata middleware, will store context-local logger extra."""
    async def dispatch(self, request, call_next):
        extra = {
            "service-name": system.project.name,
            "service-version": system.project.version,
            "request-method": request.method,
            "request-path": request.url.path
        }
        try:
            external = dict(ast.literal_eval(
                request.headers.get("X-Request-Metadata", "{}")))
        except (SyntaxError, SyntaxWarning):
            external = {}
        with logger.contextualize(**extra, **external):
            return await call_next(request)
