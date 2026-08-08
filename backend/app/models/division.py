from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.types import Timestamp, UuidPk, created_at_column, uuid_pk

if TYPE_CHECKING:
    from app.models.academic_year import AcademicYear
    from app.models.branch import Branch
    from app.models.class_ import Class
    from app.models.institution import Institution
    from app.models.student import Student


class Division(Base):
    __tablename__ = "divisions"
    __table_args__ = (
        UniqueConstraint(
            "branch_id",
            "academic_year_id",
            "name",
            name="uq_divisions_branch_academic_year_name",
        ),
        Index("ix_divisions_institution_id", "institution_id"),
        Index("ix_divisions_branch_id", "branch_id"),
        Index("ix_divisions_academic_year_id", "academic_year_id"),
    )

    id: UuidPk = uuid_pk()
    institution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    branch_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
        nullable=False,
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Timestamp = created_at_column()

    institution: Mapped[Institution] = relationship(back_populates="divisions")
    branch: Mapped[Branch] = relationship(back_populates="divisions")
    academic_year: Mapped[AcademicYear] = relationship(back_populates="divisions")
    students: Mapped[list[Student]] = relationship(back_populates="division")
    classes: Mapped[list[Class]] = relationship(back_populates="division")
