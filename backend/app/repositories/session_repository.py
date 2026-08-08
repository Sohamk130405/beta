from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session


class SessionRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, session_obj: Session) -> Session:
        self.db.add(session_obj)
        await self.db.flush()
        return session_obj

    async def get_by_token_hash(self, token_hash: str) -> Session | None:
        q = select(Session).where(Session.token_hash == token_hash)
        res = await self.db.execute(q)
        return res.scalar_one_or_none()

    async def revoke(self, session_id):
        q = update(Session).where(Session.id == session_id).values(is_revoked=True)
        await self.db.execute(q)
        await self.db.flush()
