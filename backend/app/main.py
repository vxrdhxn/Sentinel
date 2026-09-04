import logging

from fastapi import FastAPI

from backend.app.config import settings
from backend.app.database import check_database_connection
from backend.app.errors import unhandled_exception_handler
from backend.app.logging import configure_logging

configure_logging(settings.log_level)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sentinel",
    debug=settings.environment == "development",
)

logger.info("Sentinel backend initialized")
app.add_exception_handler(Exception, unhandled_exception_handler)


@app.get("/health")
def health_check() -> dict[str, str]:
    db_ok = check_database_connection()
    return {
        "status": "ok" if db_ok else "degraded",
        "database": "connected" if db_ok else "unreachable",
    }
