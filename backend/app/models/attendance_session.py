from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SessionStatus
from app.models.types import (
    MoneylessDecimal,
    Timestamp,
    UuidPk,
    created_at_column,
    latitude_column,
    longitude_column,
    meters_column,
    updated_at_column,
    uuid_pk,
)

if TYPE_CHECKING:
    from app.models.attendance import Attendance
    from app.models.class_ import Class
    from app.models.faculty import Faculty
    from app.models.verification_attempt import VerificationAttempt


class AttendanceSession(Base):
    __tablename__ = "attendance_sessions"
    __table_args__ = (
        Index("ix_attendance_sessions_class_id", "class_id"),
        Index("ix_attendance_sessions_faculty_id", "faculty_id"),
        Index("ix_attendance_sessions_status", "status"),
        Index("ix_attendance_sessions_starts_at", "starts_at"),
        Index("ix_attendance_sessions_ends_at", "ends_at"),
        Index("ix_attendance_sessions_class_status", "class_id", "status"),
        Index(
            "ix_attendance_sessions_time_status",
            "starts_at",
            "ends_at",
            "status",
        ),
    )

    id: UuidPk = uuid_pk()
    class_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    faculty_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("faculty.id", ondelete="RESTRICT"),
        nullable=False,
    )
    latitude: MoneylessDecimal = latitude_column()
    longitude: MoneylessDecimal = longitude_column()
    radius_meters: MoneylessDecimal = meters_column()
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[SessionStatus] = mapped_column(
        Enum(SessionStatus, name="session_status"),
        nullable=False,
    )
    created_at: Timestamp = created_at_column()
    updated_at: Timestamp = updated_at_column()

    class_: Mapped[Class] = relationship(back_populates="attendance_sessions")
    faculty: Mapped[Faculty] = relationship(back_populates="attendance_sessions")
    attendance_records: Mapped[list[Attendance]] = relationship(
        back_populates="session",
    )
    verification_attempts: Mapped[list[VerificationAttempt]] = relationship(
        back_populates="session",
    )
