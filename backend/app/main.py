from fastapi import FastAPI

from backend.app.config import settings

app = FastAPI(
    title="Sentinel",
    debug=settings.environment == "development",
)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
