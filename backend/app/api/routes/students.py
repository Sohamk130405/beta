from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_db
from sqlalchemy import select

from app.api.dependencies.auth import require_student, get_current_user

router = APIRouter(tags=["students"])


@router.get("/students/me")
async def get_student_me(user=Depends(require_student), db=Depends(get_db)):
    # load student profile
    from app.models.student import Student

    q = select(Student).where(Student.user_id == user.id)
    res = await db.execute(q)
    student = res.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Student profile not found.",
                }
            },
        )
    return {
        "id": str(student.id),
        "user": {
            "id": str(user.id),
            "name": user.name,
            "email": user.email,
            "profile_image_url": user.profile_image_url,
        },
        "prn": student.prn,
        "roll_number": student.roll_number,
        "branch": {"id": str(student.branch_id)},
        "division": {"id": str(student.division_id)},
        "academic_year": {"id": str(student.academic_year_id)},
    }


@router.get("/students/me/classes")
async def get_student_classes(user=Depends(require_student), db=Depends(get_db)):
    from app.models.class_ import Class
    from app.models.class_enrollment import ClassEnrollment

    q = (
        select(Class)
        .join(ClassEnrollment, Class.id == ClassEnrollment.class_id)
        .where(ClassEnrollment.student_id == user.student.id)
    )
    res = await db.execute(q)
    items = [
        {
            "id": str(c.id),
            "name": c.name,
            "subject": {"id": str(c.subject_id)},
            "faculty": {"id": str(c.faculty_id)},
            "division": {"id": str(c.division_id)},
            "academic_year": {"id": str(c.academic_year_id)},
        }
        for c in res.scalars().all()
    ]
    return {"items": items}


@router.get("/students/me/dashboard")
async def get_student_dashboard(user=Depends(require_student), db=Depends(get_db)):
    # return identity and academic information only
    from app.models.student import Student

    q = select(Student).where(Student.user_id == user.id)
    res = await db.execute(q)
    student = res.scalar_one_or_none()
    if not student:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Student profile not found.",
                }
            },
        )
    return {
        "student": {"id": str(student.id), "name": user.name, "prn": student.prn},
        "academic": {"branch": "", "division": "", "academic_year": ""},
        "classes": [],
    }
