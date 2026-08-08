from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies.auth import require_faculty
from app.api.deps import get_db
from sqlalchemy import select

from app.schemas.responses import FacultyResponse

router = APIRouter(tags=["faculty"])


@router.get("/faculty/me", response_model=FacultyResponse)
async def get_faculty_me(user=Depends(require_faculty), db=Depends(get_db)):
    from app.models.faculty import Faculty

    q = select(Faculty).where(Faculty.user_id == user.id)
    res = await db.execute(q)
    faculty = res.scalar_one_or_none()
    if not faculty:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Faculty profile not found.",
                }
            },
        )
    return {
        "id": str(faculty.id),
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "profile_image_url": user.profile_image_url,
        },
        "employee_id": faculty.employee_id,
        "department": faculty.department,
    }


@router.get("/faculty/me/classes", response_model=dict)
async def get_faculty_classes(user=Depends(require_faculty), db=Depends(get_db)):
    from app.models.faculty import Faculty
    from app.models.class_ import Class

    fres = await db.execute(select(Faculty).where(Faculty.user_id == user.id))
    faculty = fres.scalar_one_or_none()
    if not faculty:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Faculty profile not found.",
                }
            },
        )

    q = select(Class).where(Class.faculty_id == faculty.id)
    res = await db.execute(q)
    items = [
        {
            "id": str(c.id),
            "name": c.name,
            "subject": {"id": str(c.subject_id)} if c.subject_id else None,
            "division": {"id": str(c.division_id)} if c.division_id else None,
            "academic_year": {"id": str(c.academic_year_id)}
            if c.academic_year_id
            else None,
        }
        for c in res.scalars().all()
    ]
    return {"items": items}
