from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_api_v1_version() -> None:
    response = client.get("/api/v1/version")
    assert response.status_code == 200
    assert response.json() == {"api_version": "v1"}


def test_health_still_works() -> None:
    response = client.get("/health")
    assert response.status_code == 200
