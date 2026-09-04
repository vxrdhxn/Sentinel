from fastapi import FastAPI

from backend.app.api.router import api_router
from backend.app.config import settings
from backend.app.database import check_database_connection

app = FastAPI(
    title="Sentinel",
    debug=settings.environment == "development",
)

app.include_router(api_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    db_ok = check_database_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
    }
