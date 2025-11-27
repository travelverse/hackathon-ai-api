# -*- coding: utf-8 -*-
from jose import jwt
from fastapi import APIRouter, Form
from fastapi import Request, Response
from starlette import status
from starlette.responses import RedirectResponse
import system
from modules.system.security import payload

router = APIRouter()


@router.get(
    "/unlock", name="security:unlock:page", include_in_schema=False
)
async def unlock_page(request: Request, source: str = None):
    """Render unlock page"""
    # pylint: disable = E1101
    return system.runtime.templates.TemplateResponse(
        "unlock.html", {
            "request": request, "system": system,
            "source": source or f"{request.scope['root_path']}{request.app.default}"
        })


@router.post(
    "/unlock", name="security:unlock:post", include_in_schema=False,
    response_class=RedirectResponse
)
async def unlock_post(
        request: Request, response: Response,
        source: str = Form(...), token: str = Form(None)
):
    """Process unlock request"""
    security = request.app.security
    if token and token == security.token:
        encoded = jwt.encode(payload(request, security), security.secret)
        response.set_cookie(security.cookie, encoded)
        response.status_code = status.HTTP_303_SEE_OTHER
        return source

    # pylint: disable = E1101
    return system.runtime.templates.TemplateResponse(
        "unlock.html", {
            "request": request, "system": system,
            "source": source, "message": "Invalid unlock token"
        })


@router.get(
    "/lock", name="security:lock", include_in_schema=False,
    response_class=RedirectResponse
)
async def lock(request: Request, response: Response):
    """Process lock request"""
    response.delete_cookie(request.app.security.cookie)
    return f"{request.scope['root_path']}/unlock"
