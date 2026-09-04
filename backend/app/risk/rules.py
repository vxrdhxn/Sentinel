from backend.app.risk.models import (
    ExposureLevel,
    RiskSecretType,
    RiskSeverity,
    RiskSource,
)

SECRET_TYPE_SCORES: dict[RiskSecretType, float] = {
    RiskSecretType.UNKNOWN: 0.0,
    RiskSecretType.GENERIC_CREDENTIAL: 15.0,
    RiskSecretType.AUTH_TOKEN: 20.0,
    RiskSecretType.API_KEY: 25.0,
    RiskSecretType.ACCESS_TOKEN: 25.0,
    RiskSecretType.DATABASE_CREDENTIAL: 28.0,
    RiskSecretType.CLOUD_CREDENTIAL: 30.0,
    RiskSecretType.PRIVATE_KEY: 30.0,
}

EXPOSURE_SCORES: dict[ExposureLevel, float] = {
    ExposureLevel.LOCAL: 0.0,
    ExposureLevel.INTERNAL: 12.0,
    ExposureLevel.PUBLIC: 25.0,
}

SOURCE_SCORES: dict[RiskSource, float] = {
    RiskSource.GIT: 0.0,
    RiskSource.KUBERNETES: 5.0,
    RiskSource.CICD: 8.0,
    RiskSource.CLOUD: 10.0,
}

CONFIDENCE_MAX_SCORE = 20.0
HIGH_IMPACT_RESOURCE_SCORE = 15.0

SEVERITY_THRESHOLDS: tuple[tuple[float, RiskSeverity], ...] = (
    (75.0, RiskSeverity.CRITICAL),
    (50.0, RiskSeverity.HIGH),
    (25.0, RiskSeverity.MEDIUM),
    (0.0, RiskSeverity.LOW),
)
