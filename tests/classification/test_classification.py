from backend.app.classification.normalizer import _split_location, normalize_scan_result
from backend.app.classification.taxonomy import classify_secret_type
from backend.app.models.secret import SecretType
from backend.app.scanners.models import RawSecretType, ScannerMetadata, ScanResult


def _make_result(
    secret_type: RawSecretType = RawSecretType.AWS_KEY,
    location: str = "config.py:42",
    confidence: float = 0.8,
    source: str = "org/repo",
) -> ScanResult:
    return ScanResult(
        secret_type=secret_type,
        source=source,
        location=location,
        confidence=confidence,
        metadata=ScannerMetadata(scanner_name="dummy", detection_method="static"),
    )


# --- Classification of common secret categories ---


def test_classify_aws_key_maps_to_cloud_credential():
    assert classify_secret_type(RawSecretType.AWS_KEY) == SecretType.CLOUD_CREDENTIAL


def test_classify_github_token_maps_to_access_token():
    assert classify_secret_type(RawSecretType.GITHUB_TOKEN) == SecretType.ACCESS_TOKEN


def test_classify_slack_token_maps_to_auth_token():
    assert classify_secret_type(RawSecretType.SLACK_TOKEN) == SecretType.AUTH_TOKEN


def test_classify_private_key_maps_to_private_key():
    assert classify_secret_type(RawSecretType.PRIVATE_KEY) == SecretType.PRIVATE_KEY


def test_classify_generic_password_maps_to_generic_credential():
    assert classify_secret_type(RawSecretType.GENERIC_PASSWORD) == SecretType.GENERIC_CREDENTIAL


# --- Unknown/unrecognized secret types ---


def test_classify_unknown_maps_to_generic_credential():
    assert classify_secret_type(RawSecretType.UNKNOWN) == SecretType.GENERIC_CREDENTIAL


# --- Location normalization ---


def test_split_location_with_line_number():
    assert _split_location("config.py:42") == ("config.py", 42)


def test_split_location_without_line_number():
    assert _split_location("config.py") == ("config.py", None)


def test_split_location_unknown():
    assert _split_location("unknown") == (None, None)


def test_split_location_empty():
    assert _split_location("") == (None, None)


# --- Normalization of full scan results ---


def test_normalize_scan_result_basic_fields():
    result = _make_result()
    normalized = normalize_scan_result(result, detector_name="dummy")

    assert normalized.secret_type == SecretType.CLOUD_CREDENTIAL
    assert normalized.detector_name == "dummy"
    assert normalized.confidence == 0.8
    assert normalized.repository == "org/repo"
    assert normalized.file_path == "config.py"
    assert normalized.line_number == 42


def test_normalize_missing_line_number():
    result = _make_result(location="config.py")
    normalized = normalize_scan_result(result, detector_name="dummy")

    assert normalized.file_path == "config.py"
    assert normalized.line_number is None


def test_normalize_unknown_location():
    result = _make_result(location="unknown")
    normalized = normalize_scan_result(result, detector_name="dummy")

    assert normalized.file_path is None
    assert normalized.line_number is None


def test_normalize_confidence_bounds():
    low = normalize_scan_result(_make_result(confidence=0.0), detector_name="dummy")
    high = normalize_scan_result(_make_result(confidence=1.0), detector_name="dummy")

    assert low.confidence == 0.0
    assert high.confidence == 1.0


# --- Different detector/source names mapping to the same concept ---


def test_different_detectors_produce_same_secret_type():
    result_a = _make_result(secret_type=RawSecretType.AWS_KEY)
    result_b = _make_result(secret_type=RawSecretType.AWS_KEY)

    normalized_a = normalize_scan_result(result_a, detector_name="scanner-a")
    normalized_b = normalize_scan_result(result_b, detector_name="scanner-b")

    assert normalized_a.secret_type == normalized_b.secret_type
    assert normalized_a.detector_name != normalized_b.detector_name


# --- Multiple scanner results ---


def test_normalize_multiple_results_independently():
    results = [
        _make_result(secret_type=RawSecretType.AWS_KEY, location="a.py:1"),
        _make_result(secret_type=RawSecretType.SLACK_TOKEN, location="b.py:2"),
    ]
    normalized = [normalize_scan_result(r, detector_name="dummy") for r in results]

    assert normalized[0].secret_type == SecretType.CLOUD_CREDENTIAL
    assert normalized[1].secret_type == SecretType.AUTH_TOKEN
    assert normalized[0].file_path == "a.py"
    assert normalized[1].file_path == "b.py"


# --- No plaintext secret leakage ---


def test_normalized_finding_has_no_plaintext_secret_field():
    normalized = normalize_scan_result(_make_result(), detector_name="dummy")
    field_names = normalized.model_dump().keys()

    assert "value" not in field_names
    assert "secret" not in field_names
    assert "plaintext" not in field_names
