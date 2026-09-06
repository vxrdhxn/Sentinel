from datetime import UTC, datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from backend.app.scans.models import (
    ScanExecution,
    ScanExecutionStatus,
    ScanJob,
)


def test_scan_job_creation() -> None:
    target_id = "repository-a"

    job = ScanJob(target_id=target_id)

    assert job.target_id == target_id
    assert job.id is not None


def test_scan_job_accepts_custom_id() -> None:
    job_id = uuid4()

    job = ScanJob(
        id=job_id,
        target_id="repository-a",
    )

    assert job.id == job_id


def test_scan_job_rejects_empty_target_id() -> None:
    with pytest.raises(ValidationError):
        ScanJob(target_id="")


def test_scan_execution_creation() -> None:
    scan_id = uuid4()

    execution = ScanExecution(scan_id=scan_id)

    assert execution.scan_id == scan_id
    assert execution.status == ScanExecutionStatus.PENDING
    assert execution.finding_count == 0
    assert execution.started_at is None
    assert execution.completed_at is None
    assert execution.failed_at is None
    assert execution.error is None


def test_scan_execution_accepts_all_statuses() -> None:
    scan_id = uuid4()

    for status in ScanExecutionStatus:
        execution = ScanExecution(
            scan_id=scan_id,
            status=status,
        )

        assert execution.status == status


def test_scan_execution_rejects_negative_finding_count() -> None:
    with pytest.raises(ValidationError):
        ScanExecution(
            scan_id=uuid4(),
            finding_count=-1,
        )


def test_scan_execution_accepts_finding_count_zero() -> None:
    execution = ScanExecution(
        scan_id=uuid4(),
        finding_count=0,
    )

    assert execution.finding_count == 0


def test_scan_execution_accepts_finding_count() -> None:
    execution = ScanExecution(
        scan_id=uuid4(),
        finding_count=5,
    )

    assert execution.finding_count == 5


def test_scan_execution_accepts_timezone_aware_timestamps() -> None:
    timestamp = datetime.now(UTC)

    execution = ScanExecution(
        scan_id=uuid4(),
        started_at=timestamp,
        completed_at=timestamp,
        failed_at=timestamp,
    )

    assert execution.started_at == timestamp
    assert execution.completed_at == timestamp
    assert execution.failed_at == timestamp


@pytest.mark.parametrize(
    "field_name",
    ["started_at", "completed_at", "failed_at"],
)
def test_scan_execution_rejects_naive_timestamp(field_name: str) -> None:
    timestamp = datetime.now()

    with pytest.raises(ValidationError):
        ScanExecution(
            scan_id=uuid4(),
            **{field_name: timestamp},
        )


def test_scan_execution_accepts_safe_error() -> None:
    execution = ScanExecution(
        scan_id=uuid4(),
        status=ScanExecutionStatus.FAILED,
        error="scanner execution failed",
    )

    assert execution.error == "scanner execution failed"


def test_scan_execution_has_independent_ids() -> None:
    scan_id = uuid4()

    first = ScanExecution(scan_id=scan_id)
    second = ScanExecution(scan_id=scan_id)

    assert first.id != second.id
    assert first.scan_id == second.scan_id
