from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db

router = APIRouter(tags=["health"])
DatabaseSession = Depends(get_db)


class HealthResponse(BaseModel):
    status: str


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/health/db", response_model=HealthResponse)
async def database_health(
    response: Response,
    db: AsyncSession = DatabaseSession,
) -> HealthResponse:
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return HealthResponse(status="unavailable")

    return HealthResponse(status="ok")


@router.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    return HealthResponse(status="ok")
