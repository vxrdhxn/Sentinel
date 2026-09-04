from __future__ import annotations

from backend.app.scanners.models import RawSecretType, ScannerMetadata, ScanInput, ScanResult


class DummyScanner:
    """Reference implementation used to validate the Scanner contract."""

    def scan(self, scan_input: ScanInput) -> list[ScanResult]:
        return [
            ScanResult(
                secret_type=RawSecretType.UNKNOWN,
                source=scan_input.target_id,
                location=scan_input.source_path or "unknown",
                confidence=0.5,
                metadata=ScannerMetadata(
                    scanner_name="dummy",
                    detection_method="static",
                ),
            )
        ]
