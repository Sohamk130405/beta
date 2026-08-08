from datetime import timedelta, datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic import BaseModel

from app.core.config import get_settings
from app.api.deps import get_db
from app.modules.auth.service import AuthService
from app.modules.auth.utils import hash_token

router = APIRouter()


class GoogleLoginRequest(BaseModel):
    id_token: str


@router.post("/auth/google")
async def google_login(
    payload: GoogleLoginRequest, response: Response, db=Depends(get_db)
):
    settings = get_settings()
    if not settings.google_client_id:
        raise HTTPException(
            status_code=500,
            detail={
                "error": {
                    "code": "CONFIG_MISSING",
                    "message": "Google client ID not configured",
                }
            },
        )
    service = AuthService(db, settings.google_client_id)
    try:
        token_payload = await service.verify_google_id_token(payload.id_token)
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": "Invalid Google ID token",
                }
            },
        )

    user = await service.find_or_create_user(token_payload)
    raw_token, session_obj = await service.create_session_for_user(user)

    # Set cookie security depending on environment
    secure_cookie = settings.environment == "production"
    response.set_cookie(
        key="session_token",
        value=raw_token,
        httponly=True,
        secure=secure_cookie,
        samesite="lax",
        max_age=30 * 24 * 3600,
        path="/",
    )
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
    }


@router.get("/auth/me")
async def get_me(request: Request, db=Depends(get_db)):
    # extract cookie and validate session
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": "Authentication is required.",
                }
            },
        )
    token_hash = hash_token(token)
    from app.repositories.session_repository import SessionRepository
    from sqlalchemy import select
    from app.models.user import User

    repo = SessionRepository(db)
    session_obj = await repo.get_by_token_hash(token_hash)
    if (
        not session_obj
        or session_obj.is_revoked
        or session_obj.expires_at < datetime.now(timezone.utc)
    ):
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": "Authentication is required.",
                }
            },
        )
    q = select(User).where(User.id == session_obj.user_id)
    res = await db.execute(q)
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=401,
            detail={
                "error": {
                    "code": "AUTHENTICATION_REQUIRED",
                    "message": "Authentication is required.",
                }
            },
        )
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "role": user.role.value,
        "profile_image_url": user.profile_image_url,
    }


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(request: Request, response: Response, db=Depends(get_db)):
    token = request.cookies.get("session_token")
    if not token:
        response.delete_cookie("session_token", path="/")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    token_hash = hash_token(token)
    from app.repositories.session_repository import SessionRepository

    repo = SessionRepository(db)
    session_obj = await repo.get_by_token_hash(token_hash)
    if session_obj:
        await repo.revoke(session_obj.id)
    response.delete_cookie("session_token", path="/")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
