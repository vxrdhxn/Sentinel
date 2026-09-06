from backend.app.findings.models import NormalizedFinding, SecretType
from backend.app.scanners.models import RawSecretType, ScanResult


class FindingNormalizer:
    """Normalize scanner-specific results into Sentinel findings."""

    SECRET_TYPE_MAP = {
        RawSecretType.AWS_KEY: SecretType.CLOUD_CREDENTIAL,
        RawSecretType.GITHUB_TOKEN: SecretType.ACCESS_TOKEN,
        RawSecretType.SLACK_TOKEN: SecretType.AUTH_TOKEN,
        RawSecretType.PRIVATE_KEY: SecretType.PRIVATE_KEY,
        RawSecretType.GENERIC_PASSWORD: SecretType.GENERIC_CREDENTIAL,
        RawSecretType.UNKNOWN: SecretType.UNKNOWN,
    }

    def normalize(self, result: ScanResult) -> NormalizedFinding:
        return NormalizedFinding(
            secret_type=self.SECRET_TYPE_MAP[result.secret_type],
            source=result.source,
            location=result.location,
            confidence=result.confidence,
            metadata=result.metadata,
        )
