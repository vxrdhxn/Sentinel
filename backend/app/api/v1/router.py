from fastapi import APIRouter

router = APIRouter()


@router.get("/version")
def get_version() -> dict[str, str]:
    return {"api_version": "v1"}
