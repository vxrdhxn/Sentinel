from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.finding import Finding, FindingStatus
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
