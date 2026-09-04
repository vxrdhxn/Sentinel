import subprocess
from pathlib import Path

import pytest

from backend.app.scanners.git import GitScanner
from backend.app.scanners.git import scanner as git_scanner_module
from backend.app.scanners.models import RawSecretType, ScanInput


def create_git_repo(tmp_path: Path, content: str | None = None) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    if content is not None:
        (repo / ".env").write_text(content)

        subprocess.run(
            ["git", "add", "."],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )

        subprocess.run(
            [
                "git",
                "-c",
                "user.name=Sentinel Test",
                "-c",
                "user.email=test@sentinel.local",
                "commit",
                "-m",
                "synthetic test",
            ],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
        )

    return repo


@pytest.fixture
def scanner_with_fake_gitleaks(monkeypatch: pytest.MonkeyPatch) -> GitScanner:
    scanner = GitScanner(gitleaks_path="gitleaks")

    def fake_which(_: str) -> str:
        return "gitleaks"

    monkeypatch.setattr(git_scanner_module.shutil, "which", fake_which)

    return scanner


def test_detects_synthetic_secret(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = create_git_repo(
        tmp_path,
        "AWS_ACCESS_KEY_ID=AKIA4Q7X9M2P8R6T3W1Z\n"
        "AWS_SECRET_ACCESS_KEY=7fK3mP9xQ2vL8nR4tY6sD1wE5cG0hJ2k\n",
    )

    monkeypatch.setattr(
        GitScanner,
        "_run_gitleaks",
        lambda self, repository, scan_history: [
            {
                "RuleID": "aws-access-key-id",
                "File": ".env",
                "StartLine": 2,
                "EndLine": 2,
            }
        ],
    )

    scanner = GitScanner()

    results = scanner.scan(
        ScanInput(
            target_id="sentinel-test",
            content="",
            extra={"repository_path": str(repo)},
        )
    )

    assert len(results) >= 1

    result = results[0]

    assert result.source == "sentinel-test"
    assert result.location.endswith(".env:2")
    assert result.confidence == 1.0
    assert result.metadata.scanner_name == "gitleaks"
    assert result.metadata.detection_method
    assert result.secret_type in RawSecretType


def test_returns_empty_for_repository_without_secrets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = create_git_repo(
        tmp_path,
        "APP_NAME=sentinel\nENVIRONMENT=test\n",
    )

    monkeypatch.setattr(
        GitScanner,
        "_run_gitleaks",
        lambda self, repository, scan_history: [],
    )

    scanner = GitScanner()

    results = scanner.scan(
        ScanInput(
            target_id="clean-repo",
            content="",
            extra={"repository_path": str(repo)},
        )
    )

    assert results == []


def test_detects_multiple_secrets(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = create_git_repo(
        tmp_path,
        "AWS_ACCESS_KEY_ID=AKIA4Q7X9M2P8R6T3W1Z\n"
        "AWS_SECRET_ACCESS_KEY=7fK3mP9xQ2vL8nR4tY6sD1wE5cG0hJ2k\n"
        "SLACK_TOKEN=synthetic-slack-token-for-tests\n",
    )

    monkeypatch.setattr(
        GitScanner,
        "_run_gitleaks",
        lambda self, repository, scan_history: [
            {
                "RuleID": "aws-access-key-id",
                "File": ".env",
                "StartLine": 1,
                "EndLine": 1,
            },
            {
                "RuleID": "slack-token",
                "File": ".env",
                "StartLine": 3,
                "EndLine": 3,
            },
        ],
    )

    scanner = GitScanner()

    results = scanner.scan(
        ScanInput(
            target_id="multi-secret-repo",
            content="",
            extra={"repository_path": str(repo)},
        )
    )

    assert len(results) >= 2
    assert all(result.source == "multi-secret-repo" for result in results)
    assert all(result.location.startswith(".env:") for result in results)


def test_rejects_invalid_repository_path(tmp_path: Path) -> None:
    scanner = GitScanner()

    with pytest.raises(ValueError, match="repository path does not exist"):
        scanner.scan(
            ScanInput(
                target_id="invalid",
                content="",
                extra={"repository_path": str(tmp_path / "missing")},
            )
        )


def test_rejects_non_git_directory(tmp_path: Path) -> None:
    repository = tmp_path / "not-a-repo"
    repository.mkdir()

    scanner = GitScanner()

    with pytest.raises(ValueError, match="not a Git repository"):
        scanner.scan(
            ScanInput(
                target_id="non-git",
                content="",
                extra={"repository_path": str(repository)},
            )
        )


def test_empty_git_repository_returns_empty_results(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = create_git_repo(tmp_path)

    monkeypatch.setattr(
        GitScanner,
        "_run_gitleaks",
        lambda self, repository, scan_history: [],
    )

    scanner = GitScanner()

    results = scanner.scan(
        ScanInput(
            target_id="empty-repo",
            content="",
            extra={"repository_path": str(repo)},
        )
    )

    assert results == []


def test_scans_git_history(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = tmp_path / "history-repo"
    repo.mkdir()

    subprocess.run(
        ["git", "init"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    secret_file = repo / ".env"
    secret_file.write_text(
        "AWS_ACCESS_KEY_ID=synthetic-aws-access-key\n"
        "AWS_SECRET_ACCESS_KEY=synthetic-aws-secret-key\n"
    )

    subprocess.run(
        ["git", "add", "."],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Sentinel Test",
            "-c",
            "user.email=test@sentinel.local",
            "commit",
            "-m",
            "add synthetic credential",
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    secret_file.write_text("APP_NAME=sentinel\n")

    subprocess.run(
        ["git", "add", "."],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Sentinel Test",
            "-c",
            "user.email=test@sentinel.local",
            "commit",
            "-m",
            "remove synthetic credential",
        ],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    )

    captured = {}

    def fake_run_gitleaks(
        self: GitScanner,
        repository: Path,
        scan_history: bool,
    ) -> list[dict]:
        captured["scan_history"] = scan_history
        return [
            {
                "RuleID": "aws-access-key-id",
                "File": ".env",
                "StartLine": 1,
                "EndLine": 2,
            }
        ]

    monkeypatch.setattr(
        GitScanner,
        "_run_gitleaks",
        fake_run_gitleaks,
    )

    scanner = GitScanner()

    results = scanner.scan(
        ScanInput(
            target_id="history-repo",
            content="",
            extra={
                "repository_path": str(repo),
                "scan_history": True,
            },
        )
    )

    assert results
    assert captured["scan_history"] is True


def test_gitleaks_failure_does_not_expose_output(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = create_git_repo(tmp_path, "APP_NAME=sentinel\n")

    class FailedProcess:
        returncode = 2
        stdout = ""
        stderr = "sensitive repository content"

    def fake_run(*args: object, **kwargs: object) -> FailedProcess:
        return FailedProcess()

    monkeypatch.setattr(
        git_scanner_module.shutil,
        "which",
        lambda _: "gitleaks",
    )
    monkeypatch.setattr(
        git_scanner_module.subprocess,
        "run",
        fake_run,
    )

    scanner = GitScanner()

    with pytest.raises(RuntimeError, match="gitleaks scan failed") as exc_info:
        scanner.scan(
            ScanInput(
                target_id="failure-test",
                content="",
                extra={"repository_path": str(repo)},
            )
        )

    assert "sensitive repository content" not in str(exc_info.value)
