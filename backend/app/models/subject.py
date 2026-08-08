from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.types import (
    Timestamp,
    UuidPk,
    created_at_column,
    updated_at_column,
    uuid_pk,
)

if TYPE_CHECKING:
    from app.models.class_ import Class
    from app.models.institution import Institution


class Subject(Base):
    __tablename__ = "subjects"
    __table_args__ = (
        UniqueConstraint("institution_id", "code", name="uq_subjects_institution_code"),
        Index("ix_subjects_institution_id", "institution_id"),
    )

    id: UuidPk = uuid_pk()
    institution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Timestamp = created_at_column()
    updated_at: Timestamp = updated_at_column()

    institution: Mapped[Institution] = relationship(back_populates="subjects")
    classes: Mapped[list[Class]] = relationship(back_populates="subject")
