from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, String
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
    from app.models.academic_year import AcademicYear
    from app.models.attendance_session import AttendanceSession
    from app.models.class_enrollment import ClassEnrollment
    from app.models.division import Division
    from app.models.faculty import Faculty
    from app.models.institution import Institution
    from app.models.subject import Subject


class Class(Base):
    __tablename__ = "classes"
    __table_args__ = (
        Index("ix_classes_institution_id", "institution_id"),
        Index("ix_classes_subject_id", "subject_id"),
        Index("ix_classes_faculty_id", "faculty_id"),
        Index("ix_classes_division_id", "division_id"),
        Index("ix_classes_academic_year_id", "academic_year_id"),
    )

    id: UuidPk = uuid_pk()
    institution_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("institutions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    subject_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("subjects.id", ondelete="RESTRICT"),
        nullable=False,
    )
    faculty_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("faculty.id", ondelete="RESTRICT"),
        nullable=False,
    )
    division_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("divisions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    academic_year_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("academic_years.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Timestamp = created_at_column()
    updated_at: Timestamp = updated_at_column()

    institution: Mapped[Institution] = relationship(back_populates="classes")
    subject: Mapped[Subject] = relationship(back_populates="classes")
    faculty: Mapped[Faculty] = relationship(back_populates="classes")
    division: Mapped[Division] = relationship(back_populates="classes")
    academic_year: Mapped[AcademicYear] = relationship(back_populates="classes")
    enrollments: Mapped[list[ClassEnrollment]] = relationship(back_populates="class_")
    attendance_sessions: Mapped[list[AttendanceSession]] = relationship(
        back_populates="class_",
    )
