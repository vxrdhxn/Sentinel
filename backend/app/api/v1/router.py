from fastapi import APIRouter

from backend.app.api.v1.findings import router as findings_router

router = APIRouter()


@router.get("/version")
def get_version() -> dict[str, str]:
    return {"api_version": "v1"}


router.include_router(findings_router)
