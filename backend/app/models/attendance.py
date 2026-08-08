from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import AttendanceStatus
from app.models.types import (
    MoneylessDecimal,
    Timestamp,
    UuidPk,
    created_at_column,
    latitude_column,
    longitude_column,
    meters_column,
    score_column,
    uuid_pk,
)

if TYPE_CHECKING:
    from app.models.attendance_session import AttendanceSession
    from app.models.student import Student


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (
        UniqueConstraint(
            "session_id",
            "student_id",
            name="uq_attendance_session_student",
        ),
        Index("ix_attendance_session_id", "session_id"),
        Index("ix_attendance_student_id", "student_id"),
        Index("ix_attendance_marked_at", "marked_at"),
        Index("ix_attendance_student_marked_at", "student_id", "marked_at"),
    )

    id: UuidPk = uuid_pk()
    session_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("attendance_sessions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    student_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
    )
    marked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    latitude: MoneylessDecimal = latitude_column()
    longitude: MoneylessDecimal = longitude_column()
    location_accuracy: MoneylessDecimal = meters_column()
    distance_meters: MoneylessDecimal = meters_column()
    face_verified: Mapped[bool] = mapped_column(Boolean, nullable=False)
    face_score: MoneylessDecimal = score_column()
    status: Mapped[AttendanceStatus] = mapped_column(
        Enum(AttendanceStatus, name="attendance_status"),
        nullable=False,
    )
    created_at: Timestamp = created_at_column()

    session: Mapped[AttendanceSession] = relationship(
        back_populates="attendance_records",
    )
    student: Mapped[Student] = relationship(back_populates="attendance_records")
