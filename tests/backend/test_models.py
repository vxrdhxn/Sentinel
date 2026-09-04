from backend.app.models import Finding, Secret
from backend.app.models.finding import FindingSource, FindingStatus, Severity
from backend.app.models.secret import SecretType


def test_secret_model_defaults() -> None:
    secret = Secret(
        secret_type=SecretType.API_KEY,
        fingerprint="test-fingerprint",
    )

    assert secret.secret_type == SecretType.API_KEY
    assert secret.fingerprint == "test-fingerprint"
    assert secret.id is None
    assert secret.created_at is None
    assert secret.updated_at is None


def test_finding_model_fields() -> None:
    secret = Secret(
        secret_type=SecretType.API_KEY,
        fingerprint="test-fingerprint",
    )

    finding = Finding(
        secret=secret,
        source=FindingSource.GIT,
        repository="example/repo",
        file_path="config/settings.py",
        line_number=42,
        confidence=0.95,
        severity=Severity.HIGH,
        status=FindingStatus.DISCOVERED,
    )

    assert finding.secret is secret
    assert finding.source == FindingSource.GIT
    assert finding.repository == "example/repo"
    assert finding.file_path == "config/settings.py"
    assert finding.line_number == 42
    assert finding.confidence == 0.95
    assert finding.severity == Severity.HIGH
    assert finding.status == FindingStatus.DISCOVERED


def test_secret_finding_relationship() -> None:
    secret = Secret(
        secret_type=SecretType.ACCESS_TOKEN,
        fingerprint="another-fingerprint",
    )

    finding = Finding(
        secret=secret,
        source=FindingSource.GIT,
        repository="example/repo",
        confidence=0.8,
        severity=Severity.MEDIUM,
        status=FindingStatus.CONFIRMED,
    )

    assert finding in secret.findings
    assert len(secret.findings) == 1