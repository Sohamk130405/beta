from datetime import datetime
from decimal import Decimal
from typing import TypeAlias
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Numeric, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

UuidPk: TypeAlias = Mapped[UUID]
Timestamp: TypeAlias = Mapped[datetime]
MoneylessDecimal: TypeAlias = Mapped[Decimal]


def uuid_pk() -> UuidPk:
    return mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)


def created_at_column() -> Timestamp:
    return mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


def updated_at_column() -> Timestamp:
    return mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


def latitude_column() -> MoneylessDecimal:
    return mapped_column(Numeric(9, 6), nullable=False)


def longitude_column() -> MoneylessDecimal:
    return mapped_column(Numeric(9, 6), nullable=False)


def nullable_latitude_column() -> Mapped[Decimal | None]:
    return mapped_column(Numeric(9, 6))


def nullable_longitude_column() -> Mapped[Decimal | None]:
    return mapped_column(Numeric(9, 6))


def meters_column(nullable: bool = False) -> MoneylessDecimal:
    return mapped_column(Numeric(10, 2), nullable=nullable)


def score_column(nullable: bool = True) -> MoneylessDecimal:
    return mapped_column(Numeric(8, 6), nullable=nullable)
