from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies.auth import require_faculty
from app.api.deps import get_db
from sqlalchemy import select

router = APIRouter(tags=["faculty"])


@router.get("/faculty/me")
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


@router.get("/faculty/me/classes")
async def get_faculty_classes(user=Depends(require_faculty), db=Depends(get_db)):
    from app.models.class_ import Class

    q = select(Class).where(Class.faculty_id == user.faculty.id)
    res = await db.execute(q)
    items = [
        {
            "id": str(c.id),
            "name": c.name,
            "subject": {"id": str(c.subject_id)},
            "division": {"id": str(c.division_id)},
            "academic_year": {"id": str(c.academic_year_id)},
            "student_count": 0,
        }
        for c in res.scalars().all()
    ]
    return {"items": items}
