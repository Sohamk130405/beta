from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes.health import router as health_router
from app.api.routes.auth import router as auth_router
from app.api.routes.students import router as students_router
from app.api.routes.faculty import router as faculty_router
from app.core.config import get_settings
from app.db.session import dispose_engine

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    yield
    await dispose_engine()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(health_router, prefix=settings.api_v1_prefix)
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(students_router, prefix=settings.api_v1_prefix)
app.include_router(faculty_router, prefix=settings.api_v1_prefix)
if settings.environment == "development":
    from app.api.routes.dev import router as dev_router

    app.include_router(dev_router, prefix=settings.api_v1_prefix)
