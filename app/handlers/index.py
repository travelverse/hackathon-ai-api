# -*- coding: utf-8 -*-
import os
from fastapi import APIRouter, Request
from starlette.responses import FileResponse
import system

router = APIRouter()
router.app = "app"


@router.get("/", include_in_schema=False)
async def index(request: Request):
    """Webpage index"""
    # pylint: disable = E1101
    return system.runtime.templates.TemplateResponse(
        "index.html", {
            "request": request, "system": system
        })


@router.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Favicon handler"""
    return FileResponse(os.path.join(system.path.static, "favicon.ico"))
