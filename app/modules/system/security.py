# -*- coding: utf-8 -*-
from fnmatch import fnmatch
from typing import List
from pydantic import BaseModel
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, RedirectResponse
from jose import jwt


class SecuritySettings(BaseModel, extra="allow"):
    active: bool = False
    header: str = "X-Guard-Token"
    token: str = "bafaf97355b4c4f5f96dc5c3b83529a3"
    cookie: str = "_uac"
    secret: str = "79ee6ace5312de6202dfc8cc27145dd9"
    lockdown: List[str] = []


def payload(request, security):
    """Creates payload for security token.

    :param request: request object.
    :param security: security settings.
    """
    return {
        security.token: sorted(security.secret),
        request.client.host: request.headers["user-agent"]
    }


class GuardMiddleware(BaseHTTPMiddleware):
    """Security middleware, will protect:
        - endpoints with configured header and key
        - pages with simple login page using same key
    """
    def __init__(self, app, security):
        super().__init__(app)
        self.security = security
        self.skip = ["/api/lock", "/api/unlock"]
        self.lockdown = ["*/docs", "*/redoc", "*/openapi.json"] + security.lockdown

    async def dispatch(self, request, call_next):
        if self.security.active:
            if request.scope["path"] in self.skip:
                return await call_next(request)

            # pylint: disable=R1729
            if any([fnmatch(request.scope["raw_path"].decode(), lock) for lock in self.lockdown]):
                cookie = request.cookies.get(self.security.cookie)
                if cookie and jwt.decode(cookie, self.security.secret) == payload(request, self.security):
                    return await call_next(request)
                return RedirectResponse(
                    f"{request.scope['root_path']}/unlock?source={request.url.path}")

            token = request.headers.get(self.security.header)
            if not token or not token == self.security.token:
                return JSONResponse(content={"detail": "Unauthorized"}, status_code=403)

        return await call_next(request)
