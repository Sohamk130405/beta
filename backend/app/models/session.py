from __future__ import annotations

from typing import TYPE_CHECKING
from datetime import datetime, timedelta, timezone

from sqlalchemy import Boolean, DateTime, Index, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.types import (
    Timestamp,
    UuidPk,
    created_at_column,
    uuid_pk,
)

if TYPE_CHECKING:
    from app.models.user import User


class Session(Base):
    __tablename__ = "sessions"
    __table_args__ = (
        Index("ix_sessions_user_id", "user_id"),
        Index("ix_sessions_token_hash", "token_hash"),
    )

    id: UuidPk = uuid_pk()
    user_id: Mapped[str] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    token_hash: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    created_at: Timestamp = created_at_column()
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="false"
    )

    user: Mapped[User] = relationship(back_populates="sessions")

    @classmethod
    def default_expiry(cls) -> datetime:
        return datetime.now(timezone.utc) + timedelta(days=30)
