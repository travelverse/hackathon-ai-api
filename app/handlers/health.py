from fastapi import APIRouter

router = APIRouter(
    prefix="/health",
    tags=["health"],
)

router.app = "api"

@router.get("", summary="Health check")
async def health():
    return {"status": "ok"}
