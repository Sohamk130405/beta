from datetime import datetime
from typing import Optional

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.session import Session
from app.repositories.session_repository import SessionRepository
from app.models.enums import UserRole
from app.modules.auth.utils import generate_session_token, hash_token


class AuthService:
    def __init__(self, db: AsyncSession, google_client_id: str) -> None:
        self.db = db
        self.google_client_id = google_client_id
        self.session_repo = SessionRepository(db)

    async def verify_google_id_token(self, token: str) -> dict:
        # Uses google-auth to verify token signature and claims
        request = google_requests.Request()
        payload = id_token.verify_oauth2_token(token, request, self.google_client_id)
        # verify_oauth2_token raises on invalid token
        return payload

    async def find_or_create_user(self, payload: dict) -> User:
        # payload contains 'sub' as google_id
        from sqlalchemy import select

        google_id = payload.get("sub")
        email = payload.get("email")
        name = payload.get("name")
        picture = payload.get("picture")

        q = select(User).where(User.google_id == google_id)
        res = await self.db.execute(q)
        user = res.scalar_one_or_none()
        if user:
            return user

        # create user with default STUDENT role
        user = User(
            google_id=google_id,
            email=email,
            name=name or email,
            profile_image_url=picture,
            role=UserRole.STUDENT,
        )
        self.db.add(user)
        await self.db.flush()
        return user

    async def create_session_for_user(
        self, user: User, expires_at: Optional[datetime] = None
    ) -> tuple[str, Session]:
        raw_token, token_hash = generate_session_token()
        if expires_at is None:
            expires_at = Session.default_expiry()
        session_obj = Session(
            user_id=user.id, token_hash=token_hash, expires_at=expires_at
        )
        await self.session_repo.create(session_obj)
        await self.db.flush()
        return raw_token, session_obj
