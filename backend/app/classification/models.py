from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from backend.app.models.secret import SecretType


class NormalizedFinding(BaseModel):
    """Sentinel-internal representation of a classified, normalized detection.

    Produced from a raw scanner ScanResult. Shaped to be compatible with
    the Secret/Finding domain models, but does not itself persist anything.
    """

    secret_type: SecretType
    detector_name: str = Field(..., description="Name of the scanner/detector that produced this")
    confidence: float = Field(..., ge=0.0, le=1.0)
    repository: str = Field(..., description="Repository or resource the secret was found in")
    file_path: str | None = Field(default=None, description="File path, if applicable")
    line_number: int | None = Field(default=None, description="Line number, if available")
    detected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
