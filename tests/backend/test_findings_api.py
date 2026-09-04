import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.main import app
from backend.app.models.base import Base
from backend.app.models.finding import Finding, FindingSource, FindingStatus, Severity
from backend.app.models.secret import Secret, SecretType

client = TestClient(app)


@pytest.fixture
def db_session():
    engine = create_engine(settings.database_url)
    Base.metadata.create_all(engine)
    session = Session(engine)
    try:
        yield session
    finally:
        session.rollback()
        Base.metadata.drop_all(engine)
        session.close()


def _make_finding(
    db_session,
    *,
    severity=Severity.HIGH,
    status=FindingStatus.DISCOVERED,
    source=FindingSource.GIT,
    repository="org/repo-a",
    confidence=0.9,
):
    secret = Secret(secret_type=SecretType.API_KEY, fingerprint=f"fp-{repository}-{severity}")
    db_session.add(secret)
    db_session.flush()

    finding = Finding(
        secret_id=secret.id,
        source=source,
        repository=repository,
        confidence=confidence,
        severity=severity,
        status=status,
    )
    db_session.add(finding)
    db_session.flush()
    db_session.commit()
    return finding


def test_list_findings_empty(db_session):
    response = client.get("/api/v1/findings")
    assert response.status_code == 200
    body = response.json()
    assert body == {"items": [], "total": 0, "limit": 50, "offset": 0}


def test_list_findings_returns_created(db_session):
    _make_finding(db_session)
    response = client.get("/api/v1/findings")
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert len(body["items"]) == 1


def test_get_finding_success(db_session):
    finding = _make_finding(db_session)
    response = client.get(f"/api/v1/findings/{finding.id}")
    assert response.status_code == 200
    assert response.json()["id"] == str(finding.id)


def test_get_finding_not_found(db_session):
    response = client.get("/api/v1/findings/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_get_finding_invalid_id(db_session):
    response = client.get("/api/v1/findings/not-a-uuid")
    assert response.status_code == 422


def test_pagination_limit(db_session):
    for i in range(3):
        _make_finding(db_session, repository=f"org/repo-{i}")
    response = client.get("/api/v1/findings?limit=2")
    body = response.json()
    assert len(body["items"]) == 2
    assert body["total"] == 3
    assert body["limit"] == 2


def test_pagination_offset(db_session):
    for i in range(3):
        _make_finding(db_session, repository=f"org/repo-{i}")
    response = client.get("/api/v1/findings?limit=2&offset=2")
    body = response.json()
    assert len(body["items"]) == 1
    assert body["offset"] == 2


def test_filter_by_severity(db_session):
    _make_finding(db_session, severity=Severity.HIGH)
    _make_finding(db_session, severity=Severity.LOW, repository="org/other")
    response = client.get("/api/v1/findings?severity=high")
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["severity"] == "high"


def test_filter_by_status(db_session):
    _make_finding(db_session, status=FindingStatus.DISCOVERED)
    _make_finding(db_session, status=FindingStatus.REMEDIATED, repository="org/other")
    response = client.get("/api/v1/findings?status=remediated")
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["status"] == "remediated"


def test_filter_by_source(db_session):
    _make_finding(db_session, source=FindingSource.GIT)
    _make_finding(db_session, source=FindingSource.KUBERNETES, repository="org/other")
    response = client.get("/api/v1/findings?source=kubernetes")
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["source"] == "kubernetes"


def test_filter_by_repository(db_session):
    _make_finding(db_session, repository="org/target-repo")
    _make_finding(db_session, repository="org/other-repo")
    response = client.get("/api/v1/findings?repository=org/target-repo")
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["repository"] == "org/target-repo"


def test_invalid_severity_value(db_session):
    response = client.get("/api/v1/findings?severity=not-a-real-severity")
    assert response.status_code == 422


def test_invalid_limit_too_high(db_session):
    response = client.get("/api/v1/findings?limit=99999")
    assert response.status_code == 422


def test_invalid_limit_negative(db_session):
    response = client.get("/api/v1/findings?limit=-1")
    assert response.status_code == 422


def test_response_does_not_expose_secret_material(db_session):
    _make_finding(db_session)
    response = client.get("/api/v1/findings")
    body_text = response.text.lower()
    assert "fingerprint" not in body_text
    assert "secret_type" not in body_text or "fp-" not in body_text


def test_health_endpoint_unchanged():
    response = client.get("/health")
    assert response.status_code == 200
    assert "status" in response.json()