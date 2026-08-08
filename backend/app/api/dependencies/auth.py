from __future__ import annotations

from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone

from app.api.deps import get_db
from app.modules.auth.utils import hash_token
from app.repositories.session_repository import SessionRepository
from app.models.user import User


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": "Authentication is required.",
                }
            },
        )
    token_hash = hash_token(token)
    repo = SessionRepository(db)
    session_obj = await repo.get_by_token_hash(token_hash)
    if (
        not session_obj
        or session_obj.is_revoked
        or session_obj.expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": "Authentication is required.",
                }
            },
        )
    # load user
    res = await db.execute(select(User).where(User.id == session_obj.user_id))
    user = res.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {"code": "ACCOUNT_INACTIVE", "message": "Account is inactive."}
            },
        )
    return user


def require_role(role_value: str):
    async def _require_role(user: User = Depends(get_current_user)) -> User:
        if user.role.value != role_value:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "INSUFFICIENT_ROLE",
                        "message": "Insufficient role.",
                    }
                },
            )
        return user

    return _require_role


require_student = require_role("STUDENT")
require_faculty = require_role("FACULTY")
require_admin = require_role("ADMIN")
