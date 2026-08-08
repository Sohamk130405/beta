from fastapi import APIRouter, Depends, HTTPException
from app.api.deps import get_db
from sqlalchemy import select

from app.api.dependencies.auth import require_student
from app.schemas.responses import (
    StudentResponse,
    ClassResponse,
    DashboardResponse,
    BranchResponse,
    DivisionResponse,
    AcademicYearResponse,
    UserResponse,
)

router = APIRouter(tags=["students"])


@router.get("/students/me", response_model=StudentResponse)
async def get_student_me(user=Depends(require_student), db=Depends(get_db)):
    from app.models.student import Student

    q = (
        select(Student)
        .where(Student.user_id == user.id)
        .join(Student.branch)
        .join(Student.division)
        .join(Student.academic_year)
    )
    res = await db.execute(q)
    row = res.first()
    if not row:
        raise HTTPException(
            status_code=404,
            detail={
                "error": {
                    "code": "RESOURCE_NOT_FOUND",
                    "message": "Student profile not found.",
                }
            },
        )
    student = row[0]
    branch = student.branch
    division = student.division
    academic_year = student.academic_year
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
        "branch": {"id": str(branch.id), "name": branch.name, "code": branch.code},
        "division": {"id": str(division.id), "name": division.name},
        "academic_year": {"id": str(academic_year.id), "name": academic_year.name},
    }


@router.get("/students/me/classes", response_model=dict)
async def get_student_classes(user=Depends(require_student), db=Depends(get_db)):
    from app.models.class_ import Class
    from app.models.class_enrollment import ClassEnrollment
    from app.models.academic_year import AcademicYear

    # resolve student id
    from app.models.student import Student

    sres = await db.execute(select(Student).where(Student.user_id == user.id))
    student = sres.scalar_one_or_none()
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

    q = (
        select(Class)
        .join(ClassEnrollment, Class.id == ClassEnrollment.class_id)
        .join(AcademicYear, Class.academic_year)
        .where(ClassEnrollment.student_id == student.id)
        .where(AcademicYear.is_active == True)
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


@router.get("/students/me/dashboard", response_model=DashboardResponse)
async def get_student_dashboard(user=Depends(require_student), db=Depends(get_db)):
    from app.models.student import Student
    from app.models.class_ import Class
    from app.models.class_enrollment import ClassEnrollment

    sres = await db.execute(select(Student).where(Student.user_id == user.id))
    student = sres.scalar_one_or_none()
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

    branch = student.branch
    division = student.division
    academic_year = student.academic_year

    # classes for current academic year
    q = (
        select(Class)
        .join(ClassEnrollment, Class.id == ClassEnrollment.class_id)
        .where(ClassEnrollment.student_id == student.id)
        .where(Class.academic_year_id == student.academic_year_id)
    )
    cres = await db.execute(q)
    classes = [
        {
            "id": str(c.id),
            "name": c.name,
            "subject": None,
            "faculty": None,
            "division": {
                "id": str(c.division_id),
                "name": c.division.name if c.division else "",
            },
            "academic_year": {
                "id": str(c.academic_year_id),
                "name": c.academic_year.name if c.academic_year else "",
            },
        }
        for c in cres.scalars().all()
    ]

    return {
        "student": {"id": str(student.id), "name": user.name, "prn": student.prn},
        "academic": {
            "branch": {"id": str(branch.id), "name": branch.name, "code": branch.code},
            "division": {"id": str(division.id), "name": division.name},
            "academic_year": {"id": str(academic_year.id), "name": academic_year.name},
        },
        "classes": classes,
    }
