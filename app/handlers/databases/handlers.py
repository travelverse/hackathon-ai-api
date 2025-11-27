# -*- coding: utf-8 -*-
from fastapi import APIRouter, Depends, Response, Path
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from modules.system.fastapi import headers, responses
from modules.database.module import DatabaseException
from database.gateway import example
from handlers.databases import schemas

router = APIRouter(
    prefix="/databases", tags=["databases"],
    responses=responses(403, 500), dependencies=[Depends(headers)]
)
router.app = "api"


@router.get(
    "/postgres", name="databases:postgres:list",
    summary="Postgres: Examples list",
    response_model=schemas.PostgresListResponse
)
async def postgres_list():
    """Get examples list from Postgres database"""
    gateway = example.ExampleGateway()
    try:
        result = await gateway.list("postgres")
    except DatabaseException as ex:
        return JSONResponse({"code": 201, "detail": str(ex)}, status_code=550)
    return {"examples": result}


@router.get(
    "/postgres/{example_id}", name="databases:postgres:read",
    summary="Postgres: Example by ID", responses=responses(404),
    response_model=schemas.postgres.Example
)
async def postgres_read(example_id: int = Path(..., description="Example ID")):
    """Get example by ID from Postgres database"""
    gateway = example.ExampleGateway()
    try:
        result = await gateway.read("postgres", example_id)
    except DatabaseException as ex:
        return JSONResponse({"code": 201, "detail": str(ex)}, status_code=550)
    if not result:
        raise HTTPException(status_code=404, detail="Example not found")
    return result


@router.post(
    "/postgres", name="databases:postgres:create",
    summary="Postgres: Create example",
    response_model=schemas.postgres.Example, status_code=201
)
async def postgres_create(response: Response, model: schemas.postgres.Example):
    """Create new example in Postgres database"""
    gateway = example.ExampleGateway()
    try:
        result = await gateway.create("postgres", model, True)
    except DatabaseException as ex:
        return JSONResponse({"code": 201, "detail": str(ex)}, status_code=550)
    response.headers["Location"] = router.url_path_for(
        "databases:postgres:read", example_id=result.id)
    return result
