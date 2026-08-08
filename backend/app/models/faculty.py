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
    from app.models.attendance_session import AttendanceSession
    from app.models.class_ import Class
    from app.models.user import User


class Faculty(Base):
    __tablename__ = "faculty"
    __table_args__ = (
        UniqueConstraint("user_id", name="uq_faculty_user_id"),
        UniqueConstraint("employee_id", name="uq_faculty_employee_id"),
        Index("ix_faculty_user_id", "user_id"),
        Index("ix_faculty_employee_id", "employee_id"),
    )

    id: UuidPk = uuid_pk()
    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    employee_id: Mapped[str] = mapped_column(String(64), nullable=False)
    department: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Timestamp = created_at_column()
    updated_at: Timestamp = updated_at_column()

    user: Mapped[User] = relationship(back_populates="faculty")
    classes: Mapped[list[Class]] = relationship(back_populates="faculty")
    attendance_sessions: Mapped[list[AttendanceSession]] = relationship(
        back_populates="faculty",
    )
