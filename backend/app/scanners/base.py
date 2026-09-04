from __future__ import annotations

from typing import Protocol, runtime_checkable

from app.scanners.models import ScanInput, ScanResult


@runtime_checkable
class Scanner(Protocol):
    """Common interface all secret discovery scanners must implement."""

    def scan(self, scan_input: ScanInput) -> list[ScanResult]:
        """Perform discovery on the given input and return normalized results."""
        ...
