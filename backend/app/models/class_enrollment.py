from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.types import Timestamp, UuidPk, created_at_column, uuid_pk

if TYPE_CHECKING:
    from app.models.class_ import Class
    from app.models.student import Student


class ClassEnrollment(Base):
    __tablename__ = "class_enrollments"
    __table_args__ = (
        UniqueConstraint(
            "class_id",
            "student_id",
            name="uq_class_enrollments_class_student",
        ),
        Index("ix_class_enrollments_class_id", "class_id"),
        Index("ix_class_enrollments_student_id", "student_id"),
    )

    id: UuidPk = uuid_pk()
    class_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("classes.id", ondelete="RESTRICT"),
        nullable=False,
    )
    student_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("students.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_at: Timestamp = created_at_column()

    class_: Mapped[Class] = relationship(back_populates="enrollments")
    student: Mapped[Student] = relationship(back_populates="enrollments")
