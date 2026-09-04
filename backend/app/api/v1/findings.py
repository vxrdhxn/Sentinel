from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.api.v1.schemas.finding import FindingListResponse, FindingResponse
from backend.app.database import get_db
from backend.app.models.finding import FindingSource, FindingStatus, Severity
from backend.app.repositories.finding_repository import FindingRepository

router = APIRouter(prefix="/findings", tags=["findings"])

MAX_LIMIT = 200


@router.get("", response_model=FindingListResponse)
def list_findings(
    severity: Severity | None = Query(default=None),
    status: FindingStatus | None = Query(default=None),
    source: FindingSource | None = Query(default=None),
    repository: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
) -> FindingListResponse:
    repo = FindingRepository(db)
    items, total = repo.list_filtered(
        severity=severity,
        status=status,
        source=source,
        repository=repository,
        limit=limit,
        offset=offset,
    )
    return FindingListResponse(
        items=[FindingResponse.model_validate(item) for item in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{finding_id}", response_model=FindingResponse)
def get_finding(
    finding_id: UUID,
    db: Session = Depends(get_db),
) -> FindingResponse:
    repo = FindingRepository(db)
    finding = repo.get_by_id(finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found")
    return FindingResponse.model_validate(finding)
