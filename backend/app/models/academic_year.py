from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, Date, ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.types import Timestamp, UuidPk, created_at_column, uuid_pk

if TYPE_CHECKING:
    from app.models.class_ import Class
    from app.models.division import Division
    from app.models.institution import Institution
    from app.models.student import Student


class AcademicYear(Base):
    __tablename__ = "academic_years"
    __table_args__ = (
        UniqueConstraint(
            "institution_id",
            "name",
            name="uq_academic_years_institution_name",
        ),
        Index("ix_academic_years_institution_id", "institution_id"),
    )

    id: UuidPk = uuid_pk()
    institution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )
    created_at: Timestamp = created_at_column()

    institution: Mapped[Institution] = relationship(back_populates="academic_years")
    divisions: Mapped[list[Division]] = relationship(back_populates="academic_year")
    students: Mapped[list[Student]] = relationship(back_populates="academic_year")
    classes: Mapped[list[Class]] = relationship(back_populates="academic_year")
