from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Index, String
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
    from app.models.branch import Branch
    from app.models.class_ import Class
    from app.models.division import Division
    from app.models.subject import Subject


class Institution(Base):
    __tablename__ = "institutions"
    __table_args__ = (Index("ix_institutions_code", "code"),)

    id: UuidPk = uuid_pk()
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    created_at: Timestamp = created_at_column()
    updated_at: Timestamp = updated_at_column()

    academic_years: Mapped[list[AcademicYear]] = relationship(
        back_populates="institution",
    )
    branches: Mapped[list[Branch]] = relationship(back_populates="institution")
    divisions: Mapped[list[Division]] = relationship(back_populates="institution")
    subjects: Mapped[list[Subject]] = relationship(back_populates="institution")
    classes: Mapped[list[Class]] = relationship(back_populates="institution")
