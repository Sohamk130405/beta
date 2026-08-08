from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import UserRole
from app.models.types import (
    Timestamp,
    UuidPk,
    created_at_column,
    updated_at_column,
    uuid_pk,
)

if TYPE_CHECKING:
    from app.models.faculty import Faculty
    from app.models.student import Student
    from app.models.session import Session


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_google_id", "google_id"),
        Index("ix_users_email", "email"),
    )

    id: UuidPk = uuid_pk()
    google_id: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_image_url: Mapped[str | None] = mapped_column(Text)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role"),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
    )
    created_at: Timestamp = created_at_column()
    updated_at: Timestamp = updated_at_column()

    student: Mapped[Student | None] = relationship(back_populates="user")
    faculty: Mapped[Faculty | None] = relationship(back_populates="user")
    sessions: Mapped[list["Session"]] = relationship(back_populates="user")
