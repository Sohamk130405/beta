from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import VerificationStatus
from app.models.types import (
    Timestamp,
    UuidPk,
    created_at_column,
    meters_column,
    nullable_latitude_column,
    nullable_longitude_column,
    score_column,
    updated_at_column,
    uuid_pk,
)

if TYPE_CHECKING:
    from app.models.attendance_session import AttendanceSession
    from app.models.student import Student


class VerificationAttempt(Base):
    __tablename__ = "verification_attempts"
    __table_args__ = (
        Index("ix_verification_attempts_session_id", "session_id"),
        Index("ix_verification_attempts_student_id", "student_id"),
        Index("ix_verification_attempts_status", "status"),
        Index("ix_verification_attempts_expires_at", "expires_at"),
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
    status: Mapped[VerificationStatus] = mapped_column(
        Enum(VerificationStatus, name="verification_status"),
        nullable=False,
    )
    latitude: Mapped[Decimal | None] = nullable_latitude_column()
    longitude: Mapped[Decimal | None] = nullable_longitude_column()
    accuracy: Mapped[Decimal | None] = meters_column(nullable=True)
    distance_meters: Mapped[Decimal | None] = meters_column(nullable=True)
    location_verified_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
    )
    face_verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    face_score: Mapped[Decimal | None] = score_column()
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Timestamp = created_at_column()
    updated_at: Timestamp = updated_at_column()

    session: Mapped[AttendanceSession] = relationship(
        back_populates="verification_attempts",
    )
    student: Mapped[Student] = relationship(back_populates="verification_attempts")
