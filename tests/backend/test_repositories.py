import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.base import Base
from backend.app.models.finding import Finding, FindingSource, FindingStatus, Severity
from backend.app.models.secret import Secret, SecretType
from backend.app.repositories.finding_repository import FindingRepository
from backend.app.repositories.secret_repository import SecretRepository


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


def test_secret_repository_add_and_get_by_id(db_session):
    repo = SecretRepository(db_session)
    secret = Secret(secret_type=SecretType.API_KEY, fingerprint="fp-1")
    repo.add(secret)
    db_session.flush()

    fetched = repo.get_by_id(secret.id)
    assert fetched is not None
    assert fetched.fingerprint == "fp-1"


def test_secret_repository_get_by_fingerprint(db_session):
    repo = SecretRepository(db_session)
    repo.add(Secret(secret_type=SecretType.PRIVATE_KEY, fingerprint="fp-unique"))
    db_session.flush()

    found = repo.get_by_fingerprint("fp-unique")
    assert found is not None
    assert found.secret_type == SecretType.PRIVATE_KEY


def test_secret_repository_get_by_fingerprint_missing(db_session):
    repo = SecretRepository(db_session)
    assert repo.get_by_fingerprint("does-not-exist") is None


def test_finding_repository_list_by_secret(db_session):
    secret_repo = SecretRepository(db_session)
    finding_repo = FindingRepository(db_session)

    secret = secret_repo.add(Secret(secret_type=SecretType.API_KEY, fingerprint="fp-2"))
    db_session.flush()

    finding = Finding(
        secret_id=secret.id,
        source=FindingSource.GIT,
        repository="org/repo",
        confidence=0.9,
        severity=Severity.HIGH,
        status=FindingStatus.DISCOVERED,
    )
    finding_repo.add(finding)
    db_session.flush()

    results = finding_repo.list_by_secret(secret.id)
    assert len(results) == 1
    assert results[0].repository == "org/repo"


def test_finding_repository_list_by_status_no_matches(db_session):
    finding_repo = FindingRepository(db_session)
    results = finding_repo.list_by_status(FindingStatus.REMEDIATED)
    assert results == []
