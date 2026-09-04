from enum import StrEnum

from pydantic import BaseModel, Field


class RiskSecretType(StrEnum):
    API_KEY = "api_key"
    ACCESS_TOKEN = "access_token"
    CLOUD_CREDENTIAL = "cloud_credential"
    PRIVATE_KEY = "private_key"
    DATABASE_CREDENTIAL = "database_credential"
    AUTH_TOKEN = "auth_token"
    GENERIC_CREDENTIAL = "generic_credential"
    UNKNOWN = "unknown"


class ExposureLevel(StrEnum):
    LOCAL = "local"
    INTERNAL = "internal"
    PUBLIC = "public"


class RiskSource(StrEnum):
    GIT = "git"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"
    CICD = "cicd"


class RiskSeverity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskFindingInput(BaseModel):
    secret_type: RiskSecretType
    confidence: float = Field(ge=0.0, le=1.0)
    exposure: ExposureLevel
    source: RiskSource
    high_impact_resource: bool = False


class RiskBreakdown(BaseModel):
    secret_type: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0)
    exposure: float = Field(ge=0.0)
    source: float = Field(ge=0.0)
    resource_impact: float = Field(ge=0.0)


class RiskScoreResult(BaseModel):
    score: float = Field(ge=0.0, le=100.0)
    severity: RiskSeverity
    breakdown: RiskBreakdown
