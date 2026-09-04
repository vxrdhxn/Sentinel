from __future__ import annotations

from backend.app.models.secret import SecretType
from backend.app.scanners.models import RawSecretType

# Deterministic mapping from raw scanner detection types to Sentinel's
# domain-level secret taxonomy. Unrecognized raw types fall back to
# GENERIC_CREDENTIAL rather than raising, so classification never fails
# outright on an unfamiliar detector output.
_RAW_TO_DOMAIN: dict[RawSecretType, SecretType] = {
    RawSecretType.AWS_KEY: SecretType.CLOUD_CREDENTIAL,
    RawSecretType.GITHUB_TOKEN: SecretType.ACCESS_TOKEN,
    RawSecretType.SLACK_TOKEN: SecretType.AUTH_TOKEN,
    RawSecretType.PRIVATE_KEY: SecretType.PRIVATE_KEY,
    RawSecretType.GENERIC_PASSWORD: SecretType.GENERIC_CREDENTIAL,
    RawSecretType.UNKNOWN: SecretType.GENERIC_CREDENTIAL,
}


def classify_secret_type(raw_type: RawSecretType) -> SecretType:
    """Map a raw scanner detection type to Sentinel's domain SecretType.

    Falls back to GENERIC_CREDENTIAL for any raw type without an explicit
    mapping, so new/unrecognized scanner output is handled safely.
    """
    return _RAW_TO_DOMAIN.get(raw_type, SecretType.GENERIC_CREDENTIAL)
