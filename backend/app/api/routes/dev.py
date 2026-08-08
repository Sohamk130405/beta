from datetime import timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy import select

from app.api.deps import get_db
import os
from app.core.config import get_settings
from app.modules.auth.utils import generate_session_token
from app.models.enums import UserRole

router = APIRouter(tags=["dev"])


class DevUserCreate(BaseModel):
    email: EmailStr
    name: str
    role: str | None = None  # 'student', 'faculty' or 'admin'
    # student-specific optional fields
    prn: str | None = None
    roll_number: str | None = None
    branch_id: str | None = None
    division_id: str | None = None
    academic_year_id: str | None = None
    # faculty-specific optional fields
    employee_id: str | None = None
    department: str | None = None


@router.post("/dev/provision-user")
async def provision_user(payload: DevUserCreate, db=Depends(get_db)):
    settings = get_settings()
    env = os.getenv("ENVIRONMENT", settings.environment)
    if env != "development":
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
        # determine role
        role = UserRole.STUDENT
        if payload.role:
            r = payload.role.strip().upper()
            if r == "FACULTY":
                role = UserRole.FACULTY
            elif r == "ADMIN":
                role = UserRole.ADMIN
            else:
                role = UserRole.STUDENT

        user = User(
            google_id=f"dev:{payload.email}",
            email=payload.email,
            name=payload.name,
            role=role,
        )
        db.add(user)
        await db.flush()
    else:
        # update role if requested
        if payload.role:
            r = payload.role.strip().upper()
            if r in ("STUDENT", "FACULTY", "ADMIN"):
                user.role = UserRole[r]
                await db.flush()

    # Optionally create profile records
    if payload.role == "student":
        # require minimal fields
        required = (
            payload.prn,
            payload.roll_number,
            payload.branch_id,
            payload.division_id,
            payload.academic_year_id,
        )
        if not all(required):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "code": "INVALID_PAYLOAD",
                        "message": "Missing student profile fields.",
                    }
                },
            )
        from app.models.student import Student

        # referenced academic entity existence will be validated by DB constraints
        # create student
        student = Student(
            user_id=user.id,
            prn=payload.prn,
            roll_number=payload.roll_number,
            branch_id=payload.branch_id,
            division_id=payload.division_id,
            academic_year_id=payload.academic_year_id,
        )
        db.add(student)
        await db.flush()
    elif payload.role == "faculty":
        if not (payload.employee_id and payload.department):
            raise HTTPException(
                status_code=422,
                detail={
                    "error": {
                        "code": "INVALID_PAYLOAD",
                        "message": "Missing faculty profile fields.",
                    }
                },
            )
        from app.models.faculty import Faculty

        faculty = Faculty(
            user_id=user.id,
            employee_id=payload.employee_id,
            department=payload.department,
        )
        db.add(faculty)
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
