from enum import StrEnum
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from backend.app.models.finding import Finding


class SecretType(StrEnum):
    API_KEY = "api_key"
    ACCESS_TOKEN = "access_token"
    CLOUD_CREDENTIAL = "cloud_credential"
    PRIVATE_KEY = "private_key"
    DATABASE_CREDENTIAL = "database_credential"
    AUTH_TOKEN = "auth_token"
    GENERIC_CREDENTIAL = "generic_credential"


class Secret(UUIDMixin, TimestampMixin, Base):
    __tablename__ = "secrets"

    secret_type: Mapped[SecretType] = mapped_column(String(50), nullable=False)
    fingerprint: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        index=True,
    )

    findings: Mapped[list["Finding"]] = relationship(
        back_populates="secret",
        cascade="all, delete-orphan",
    )
