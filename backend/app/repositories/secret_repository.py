from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models.secret import Secret
from backend.app.repositories.base import BaseRepository


class SecretRepository(BaseRepository[Secret]):
    model = Secret

    def __init__(self, session: Session) -> None:
        super().__init__(session)

    def get_by_fingerprint(self, fingerprint: str) -> Secret | None:
        stmt = select(Secret).where(Secret.fingerprint == fingerprint)
        return self.session.execute(stmt).scalar_one_or_none()
