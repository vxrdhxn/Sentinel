from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.app.models.finding import Finding, FindingSource, FindingStatus, Severity
from backend.app.repositories.base import BaseRepository


class FindingRepository(BaseRepository[Finding]):
    model = Finding

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def list_by_secret(self, secret_id: UUID) -> list[Finding]:
        stmt = select(Finding).where(Finding.secret_id == secret_id)
        return list(self.session.execute(stmt).scalars().all())

    def list_by_status(self, status: FindingStatus) -> list[Finding]:
        stmt = select(Finding).where(Finding.status == status)
        return list(self.session.execute(stmt).scalars().all())

    def list_filtered(
        self,
        *,
        severity: Severity | None = None,
        status: FindingStatus | None = None,
        source: FindingSource | None = None,
        repository: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Finding], int]:
        """List findings with optional filters and pagination.

        Returns (items, total_count); total_count reflects the filtered
        count before pagination is applied, for building paginated responses.
        """
        stmt = select(Finding)
        count_stmt = select(func.count()).select_from(Finding)

        if severity is not None:
            stmt = stmt.where(Finding.severity == severity)
            count_stmt = count_stmt.where(Finding.severity == severity)
        if status is not None:
            stmt = stmt.where(Finding.status == status)
            count_stmt = count_stmt.where(Finding.status == status)
        if source is not None:
            stmt = stmt.where(Finding.source == source)
            count_stmt = count_stmt.where(Finding.source == source)
        if repository is not None:
            stmt = stmt.where(Finding.repository == repository)
            count_stmt = count_stmt.where(Finding.repository == repository)

        total = self.session.execute(count_stmt).scalar_one()

        stmt = stmt.order_by(Finding.created_at.desc()).limit(limit).offset(offset)
        items = list(self.session.execute(stmt).scalars().all())

        return items, total