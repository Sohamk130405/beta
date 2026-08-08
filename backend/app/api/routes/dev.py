from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

from app.api.deps import get_db
from app.core.config import get_settings
from app.modules.auth.utils import generate_session_token
from app.models.enums import UserRole

router = APIRouter(tags=["dev"])


class DevUserCreate(BaseModel):
    email: EmailStr
    name: str


@router.post("/dev/provision-user")
async def provision_user(payload: DevUserCreate, db=Depends(get_db)):
    settings = get_settings()
    if settings.environment != "development":
        raise HTTPException(
            status_code=403,
            detail={
                "error": {"code": "FORBIDDEN", "message": "Dev endpoints are disabled."}
            },
        )

    from app.models.user import User
    from app.models.session import Session

    # Find or create user
    q = select(User).where(User.email == payload.email)
    res = await db.execute(q)
    user = res.scalar_one_or_none()
    if not user:
        user = User(
            google_id=f"dev:{payload.email}",
            email=payload.email,
            name=payload.name,
            role=UserRole.STUDENT,
        )
        db.add(user)
        await db.flush()

    # create server-side session and return raw token for manual testing (dev only)
    raw_token, token_hash = generate_session_token()
    session_obj = Session(
        user_id=user.id, token_hash=token_hash, expires_at=Session.default_expiry()
    )
    db.add(session_obj)
    await db.flush()
    await db.commit()

    return {
        "raw_token": raw_token,
        "user": {"id": str(user.id), "email": user.email, "name": user.name},
    }
