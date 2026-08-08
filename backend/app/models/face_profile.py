from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from pgvector.sqlalchemy import Vector
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
    from app.models.student import Student


class FaceProfile(Base):
    __tablename__ = "face_profiles"
    __table_args__ = (
        UniqueConstraint("student_id", name="uq_face_profiles_student_id"),
        Index("ix_face_profiles_student_id", "student_id"),
    )

    id: UuidPk = uuid_pk()
    student_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
    )
    embedding: Mapped[list[float]] = mapped_column(Vector(), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_version: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Timestamp = created_at_column()
    updated_at: Timestamp = updated_at_column()

    student: Mapped[Student] = relationship(back_populates="face_profile")
