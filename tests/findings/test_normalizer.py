import pytest
from pydantic import ValidationError

from backend.app.findings.models import NormalizedFinding, SecretType
from backend.app.findings.normalizer import FindingNormalizer
from backend.app.scanners.models import (
    RawSecretType,
    ScannerMetadata,
    ScanResult,
)


def create_scan_result(
    secret_type: RawSecretType,
    source: str = "test-repository",
    location: str = ".env:10",
    confidence: float = 0.9,
) -> ScanResult:
    return ScanResult(
        secret_type=secret_type,
        source=source,
        location=location,
        confidence=confidence,
        metadata=ScannerMetadata(
            scanner_name="test-scanner",
            scanner_version="1.0.0",
            detection_method="test-rule",
        ),
    )


def test_normalizes_aws_key() -> None:
    result = FindingNormalizer().normalize(create_scan_result(RawSecretType.AWS_KEY))

    assert result.secret_type == SecretType.CLOUD_CREDENTIAL


def test_normalizes_github_token() -> None:
    result = FindingNormalizer().normalize(create_scan_result(RawSecretType.GITHUB_TOKEN))

    assert result.secret_type == SecretType.ACCESS_TOKEN


def test_normalizes_slack_token() -> None:
    result = FindingNormalizer().normalize(create_scan_result(RawSecretType.SLACK_TOKEN))

    assert result.secret_type == SecretType.AUTH_TOKEN


def test_normalizes_private_key() -> None:
    result = FindingNormalizer().normalize(create_scan_result(RawSecretType.PRIVATE_KEY))

    assert result.secret_type == SecretType.PRIVATE_KEY


def test_normalizes_generic_password() -> None:
    result = FindingNormalizer().normalize(create_scan_result(RawSecretType.GENERIC_PASSWORD))

    assert result.secret_type == SecretType.GENERIC_CREDENTIAL


def test_normalizes_unknown() -> None:
    result = FindingNormalizer().normalize(create_scan_result(RawSecretType.UNKNOWN))

    assert result.secret_type == SecretType.UNKNOWN


def test_preserves_source() -> None:
    result = FindingNormalizer().normalize(
        create_scan_result(RawSecretType.AWS_KEY, source="repository-a")
    )

    assert result.source == "repository-a"


def test_preserves_location() -> None:
    result = FindingNormalizer().normalize(
        create_scan_result(RawSecretType.AWS_KEY, location="config/settings.py:42")
    )

    assert result.location == "config/settings.py:42"


def test_preserves_confidence() -> None:
    result = FindingNormalizer().normalize(
        create_scan_result(RawSecretType.AWS_KEY, confidence=0.73)
    )

    assert result.confidence == 0.73


def test_preserves_scanner_metadata() -> None:
    result = FindingNormalizer().normalize(create_scan_result(RawSecretType.AWS_KEY))

    assert result.metadata.scanner_name == "test-scanner"
    assert result.metadata.scanner_version == "1.0.0"
    assert result.metadata.detection_method == "test-rule"


def test_result_is_normalized_finding() -> None:
    result = FindingNormalizer().normalize(create_scan_result(RawSecretType.GITHUB_TOKEN))

    assert isinstance(result, NormalizedFinding)


def test_normalization_is_deterministic() -> None:
    scan_result = create_scan_result(RawSecretType.AWS_KEY)

    first = FindingNormalizer().normalize(scan_result)
    second = FindingNormalizer().normalize(scan_result)

    assert first == second


def test_rejects_confidence_below_zero() -> None:
    with pytest.raises(ValidationError):
        create_scan_result(
            RawSecretType.AWS_KEY,
            confidence=-0.1,
        )


def test_rejects_confidence_above_one() -> None:
    with pytest.raises(ValidationError):
        create_scan_result(
            RawSecretType.AWS_KEY,
            confidence=1.1,
        )


def test_rejects_empty_source() -> None:
    with pytest.raises(ValidationError):
        FindingNormalizer().normalize(
            create_scan_result(
                RawSecretType.AWS_KEY,
                source="",
            )
        )


def test_rejects_empty_location() -> None:
    with pytest.raises(ValidationError):
        FindingNormalizer().normalize(
            create_scan_result(
                RawSecretType.AWS_KEY,
                location="",
            )
        )


def test_normalized_finding_does_not_contain_secret_material() -> None:
    result = FindingNormalizer().normalize(create_scan_result(RawSecretType.AWS_KEY))

    assert set(result.model_dump()) == {
        "secret_type",
        "source",
        "location",
        "confidence",
        "metadata",
    }
