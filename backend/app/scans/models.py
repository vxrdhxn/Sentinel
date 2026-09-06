from datetime import datetime
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class ScanExecutionStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ScanJob(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    target_id: str = Field(min_length=1)
    status: ScanExecutionStatus = ScanExecutionStatus.PENDING


class ScanExecution(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    scan_id: UUID
    status: ScanExecutionStatus = ScanExecutionStatus.PENDING
    started_at: datetime | None = None
    completed_at: datetime | None = None
    failed_at: datetime | None = None
    finding_count: int = Field(default=0, ge=0)
    error: str | None = None

    @field_validator("started_at", "completed_at", "failed_at")
    @classmethod
    def validate_timezone_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return value
