from enum import StrEnum

from pydantic import BaseModel, Field

from backend.app.scanners.models import ScannerMetadata


class SecretType(StrEnum):
    API_KEY = "api_key"
    ACCESS_TOKEN = "access_token"
    CLOUD_CREDENTIAL = "cloud_credential"
    PRIVATE_KEY = "private_key"
    DATABASE_CREDENTIAL = "database_credential"
    AUTH_TOKEN = "auth_token"
    GENERIC_CREDENTIAL = "generic_credential"
    UNKNOWN = "unknown"


class NormalizedFinding(BaseModel):
    secret_type: SecretType
    source: str = Field(min_length=1)
    location: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    metadata: ScannerMetadata
