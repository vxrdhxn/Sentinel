from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from backend.app.scanners.base import Scanner
from backend.app.scanners.models import (
    RawSecretType,
    ScanInput,
    ScannerMetadata,
    ScanResult,
)


class GitScanner(Scanner):
    """Secret scanner for local Git repositories."""

    def __init__(self, gitleaks_path: str | None = None) -> None:
        self.gitleaks_path = gitleaks_path

    def scan(self, scan_input: ScanInput) -> list[ScanResult]:
        repository_path = scan_input.extra.get("repository_path")

        if not repository_path:
            raise ValueError("repository_path is required")

        repository = Path(repository_path)

        if not repository.exists():
            raise ValueError("repository path does not exist")

        if not repository.is_dir():
            raise ValueError("repository path must be a directory")

        if not (repository / ".git").exists():
            raise ValueError("repository path is not a Git repository")

        scan_history = scan_input.extra.get("scan_history", False)
        detections = self._run_gitleaks(repository, scan_history)

        return [
            self._normalize_detection(
                detection,
                scan_input,
            )
            for detection in detections
        ]

    def _run_gitleaks(
        self,
        repository: Path,
        scan_history: bool,
    ) -> list[dict]:
        executable = self.gitleaks_path or shutil.which("gitleaks")

        if executable is None:
            raise RuntimeError("gitleaks executable not found")

        command = [
            executable,
            "git",
            "--report-format",
            "json",
            "--report-path",
            "-",
            str(repository),
        ]

        if scan_history:
            command.append("--log-opts=--all")

        process = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )

        if process.returncode not in (0, 1):
            raise RuntimeError("gitleaks scan failed")

        if not process.stdout.strip():
            return []

        return json.loads(process.stdout)

    def _normalize_detection(
        self,
        detection: dict,
        scan_input: ScanInput,
    ) -> ScanResult:
        rule_id = detection.get("RuleID", "unknown")
        file_path = detection.get("File", "unknown")
        start_line = detection.get("StartLine")

        location = file_path
        if start_line is not None:
            location = f"{file_path}:{start_line}"

        return ScanResult(
            secret_type=self._map_secret_type(rule_id),
            source=scan_input.target_id,
            location=location,
            confidence=1.0,
            metadata=ScannerMetadata(
                scanner_name="gitleaks",
                scanner_version="8.30.1",
                detection_method=rule_id,
            ),
        )

    def _map_secret_type(self, rule_id: str) -> RawSecretType:
        rule = rule_id.lower()

        if "aws" in rule:
            return RawSecretType.AWS_KEY

        if "github" in rule:
            return RawSecretType.GITHUB_TOKEN

        if "slack" in rule:
            return RawSecretType.SLACK_TOKEN

        if "private-key" in rule or "private_key" in rule:
            return RawSecretType.PRIVATE_KEY

        if "password" in rule:
            return RawSecretType.GENERIC_PASSWORD

        return RawSecretType.UNKNOWN
