from __future__ import annotations

from backend.app.classification.models import NormalizedFinding
from backend.app.classification.taxonomy import classify_secret_type
from backend.app.scanners.models import ScanResult


def _split_location(location: str) -> tuple[str | None, int | None]:
    """Split a scanner location string like "config.py:42" into
    (file_path, line_number). Falls back to (location, None) if there's
    no parseable line number, and (None, None) for "unknown"/empty input.
    """
    if not location or location == "unknown":
        return None, None

    if ":" in location:
        path_part, _, line_part = location.rpartition(":")
        if line_part.isdigit():
            return path_part, int(line_part)

    return location, None


def normalize_scan_result(result: ScanResult, *, detector_name: str) -> NormalizedFinding:
    """Convert a raw scanner ScanResult into a NormalizedFinding.

    Classification and normalization live here so downstream components
    (persistence, risk assessment, API) never need to understand
    scanner-specific output shapes or terminology.
    """
    file_path, line_number = _split_location(result.location)

    return NormalizedFinding(
        secret_type=classify_secret_type(result.secret_type),
        detector_name=detector_name,
        confidence=result.confidence,
        repository=result.source,
        file_path=file_path,
        line_number=line_number,
    )
