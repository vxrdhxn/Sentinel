from enum import StrEnum
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.app.models.secret import Secret


class FindingSource(StrEnum):
    GIT = "git"
    KUBERNETES = "kubernetes"
    CLOUD = "cloud"
    CICD = "cicd"


class FindingStatus(StrEnum):
    DISCOVERED = "discovered"
    CONFIRMED = "confirmed"
    FALSE_POSITIVE = "false_positive"
    REMEDIATED = "remediated"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Finding(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "findings"

    secret_id: Mapped[UUID] = mapped_column(
        ForeignKey("secrets.id"),
        nullable=False,
        index=True,
    )
    source: Mapped[FindingSource] = mapped_column(String(30), nullable=False)
    repository: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str | None] = mapped_column(String(1000))
    line_number: Mapped[int | None] = mapped_column(Integer)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[Severity] = mapped_column(String(20), nullable=False)
    status: Mapped[FindingStatus] = mapped_column(String(30), nullable=False)

    secret: Mapped["Secret"] = relationship(back_populates="findings")
