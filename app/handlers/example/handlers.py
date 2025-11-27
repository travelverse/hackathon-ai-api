# -*- coding: utf-8 -*-
from fastapi import FastAPI, APIRouter, Depends
from modules.system.fastapi import headers, responses
from handlers.example import schemas
import system

router = APIRouter(
    prefix="/example", tags=["example"],
    responses=responses(403, 500), dependencies=[Depends(headers)]
)
router.app = "api"

subapp = FastAPI(
    title=system.project.name, version=system.project.version,
    responses=responses(403, 500), dependencies=[Depends(headers)]
)
subapp.name = "subapp"
subapp.path = "/subapp"
subapp.default = "/subapp"


@router.post(
    "/echo", name="example:echo", summary="Echo request data",
    response_model=schemas.SampleEchoResponse
)
async def echo(data: schemas.SampleEchoRequest):
    """Just returns request data, nothing more"""
    return schemas.SampleEchoRequest(**data.dict())


@subapp.get(
    "/hello", name="subapp:hello", summary="Hello from subapp",
    response_model=schemas.SubappHelloResponse
)
async def hello():
    """This is how sub-apps works..."""
    return {"message": "Hello!"}
