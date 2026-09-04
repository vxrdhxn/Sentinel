from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RawSecretType(str, Enum):
    AWS_KEY = "aws_key"
    GITHUB_TOKEN = "github_token"
    SLACK_TOKEN = "slack_token"
    PRIVATE_KEY = "private_key"
    GENERIC_PASSWORD = "generic_password"
    UNKNOWN = "unknown"


class ScanInput(BaseModel):
    """What a scanner receives to perform discovery."""

    target_id: str = Field(..., description="Identifier for the scan target, e.g. repo name")
    content: str = Field(..., description="Raw content to scan")
    source_path: str | None = Field(default=None, description="File path or location")
    extra: dict[str, Any] = Field(default_factory=dict, description="Scanner-specific context")


class ScannerMetadata(BaseModel):
    """Metadata identifying which scanner produced a detection and how."""

    scanner_name: str
    scanner_version: str = "0.1.0"
    detection_method: str


class ScanResult(BaseModel):
    """Normalized output contract for a single detection."""

    secret_type: RawSecretType
    source: str = Field(..., description="Where this was found, e.g. repo name")
    location: str = Field(..., description="File path, line number, or commit ref")
    confidence: float = Field(..., ge=0.0, le=1.0)
    metadata: ScannerMetadata
