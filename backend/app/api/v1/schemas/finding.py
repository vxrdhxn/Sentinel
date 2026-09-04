from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from backend.app.models.finding import FindingSource, FindingStatus, Severity


class FindingResponse(BaseModel):
    """Public API representation of a Finding. Excludes secret material."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    secret_id: UUID
    source: FindingSource
    repository: str
    file_path: str | None
    line_number: int | None
    confidence: float
    severity: Severity
    status: FindingStatus
    created_at: datetime
    updated_at: datetime


class FindingListResponse(BaseModel):
    """Paginated collection of findings."""

    items: list[FindingResponse]
    total: int
    limit: int
    offset: int
