from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.app.errors import unhandled_exception_handler
from backend.app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_health_check() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "connected"}


def test_unhandled_exception() -> None:
    test_app = FastAPI(debug=False)
    test_app.add_exception_handler(Exception, unhandled_exception_handler)

    @test_app.get("/test-error")
    def test_error() -> None:
        raise RuntimeError("test exception")

    test_client = TestClient(test_app, raise_server_exceptions=False)

    response = test_client.get("/test-error")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
