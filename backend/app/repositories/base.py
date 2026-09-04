from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Shared CRUD operations for a single SQLAlchemy model.

    Receives an existing Session; does not create or manage its own
        engine/session, and does not commit; the caller owns the
    transaction boundary.
    """

    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_by_id(self, id_: UUID) -> ModelT | None:
        return self.session.get(self.model, id_)

    def list_all(self) -> list[ModelT]:
        return list(self.session.execute(select(self.model)).scalars().all())

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        self.session.flush()
        return instance

    def delete(self, instance: ModelT) -> None:
        self.session.delete(instance)
        self.session.flush()
