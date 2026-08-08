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
    from app.models.academic_year import AcademicYear
    from app.models.attendance import Attendance
    from app.models.branch import Branch
    from app.models.class_enrollment import ClassEnrollment
    from app.models.division import Division
    from app.models.face_profile import FaceProfile
    from app.models.user import User
    from app.models.verification_attempt import VerificationAttempt


class Student(Base):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_students_user_id"),
        UniqueConstraint("prn", name="uq_students_prn"),
        Index("ix_students_user_id", "user_id"),
        Index("ix_students_prn", "prn"),
        Index("ix_students_branch_id", "branch_id"),
        Index("ix_students_division_id", "division_id"),
        Index("ix_students_academic_year_id", "academic_year_id"),
    )

    id: UuidPk = uuid_pk()
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    prn: Mapped[str] = mapped_column(String(64), nullable=False)
    roll_number: Mapped[str] = mapped_column(String(64), nullable=False)
    branch_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("branches.id", ondelete="RESTRICT"),
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
    created_at: Timestamp = created_at_column()
    updated_at: Timestamp = updated_at_column()

    user: Mapped[User] = relationship(back_populates="student")
    branch: Mapped[Branch] = relationship(back_populates="students")
    division: Mapped[Division] = relationship(back_populates="students")
    academic_year: Mapped[AcademicYear] = relationship(back_populates="students")
    enrollments: Mapped[list[ClassEnrollment]] = relationship(back_populates="student")
    face_profile: Mapped[FaceProfile | None] = relationship(back_populates="student")
    attendance_records: Mapped[list[Attendance]] = relationship(
        back_populates="student",
    )
    verification_attempts: Mapped[list[VerificationAttempt]] = relationship(
        back_populates="student",
    )
