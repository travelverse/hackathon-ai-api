# -*- coding: utf-8 -*-
from fastapi import APIRouter
from pydantic import BaseModel, Field
from modules.system.fastapi import responses
import system

router = APIRouter(
    tags=["general"], responses=responses(403, 500)
)
router.app = "api"


class IndexResponse(BaseModel):
    service: str = Field(..., description="Service name", example="service")
    version: str = Field(..., description="Service version", example="1.0.0")


@router.get(
    "/", name="api:index", summary="API index",
    response_model=IndexResponse
)
async def index():
    """API index"""
    return {
        "service": system.project.name,
        "version": system.project.version
    }
