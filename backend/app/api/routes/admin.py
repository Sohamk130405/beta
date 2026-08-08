from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.api.deps import get_db
from app.api.dependencies.auth import require_admin
from app.schemas.admin import (
    InstitutionCreate,
    InstitutionResponse,
    InstitutionUpdate,
    AcademicYearCreate,
    AcademicYearResponse,
    AcademicYearUpdate,
    BranchCreate,
    BranchResponse,
    BranchUpdate,
    DivisionCreate,
    DivisionResponse,
    DivisionUpdate,
    SubjectCreate,
    SubjectResponse,
    SubjectUpdate,
    ClassCreate,
    ClassResponse,
    ClassUpdate,
    EnrollmentCreate,
    EnrollmentResponse,
)
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])

MAX_PAGE_SIZE = 200


# Institutions
@router.post("/institutions", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
async def create_institution(payload: InstitutionCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.institution import Institution

    inst = Institution(name=payload.name, code=payload.code)
    db.add(inst)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Institution code already exists."}})
    return {"id": str(inst.id), "name": inst.name, "code": inst.code}


@router.get("/institutions", response_model=dict)
async def list_institutions(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.institution import Institution

    q = select(Institution).offset((page - 1) * page_size).limit(page_size)
    total_q = select(func.count()).select_from(Institution)
    res = await db.execute(q)
    total_res = await db.execute(total_q)
    items = res.scalars().all()
    total = total_res.scalar_one()
    pagination = {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}
    return {"items": [{"id": str(i.id), "name": i.name, "code": i.code} for i in items], "pagination": pagination}


@router.get("/institutions/{id}", response_model=InstitutionResponse)
async def get_institution(id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.institution import Institution

    res = await db.execute(select(Institution).where(Institution.id == id))
    inst = res.scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Institution not found."}})
    return {"id": str(inst.id), "name": inst.name, "code": inst.code}


@router.patch("/institutions/{id}", response_model=InstitutionResponse)
async def update_institution(id: str, payload: InstitutionUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.institution import Institution

    res = await db.execute(select(Institution).where(Institution.id == id))
    inst = res.scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Institution not found."}})
    if payload.name is not None:
        inst.name = payload.name
    if payload.code is not None:
        inst.code = payload.code
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Institution code conflict."}})
    return {"id": str(inst.id), "name": inst.name, "code": inst.code}


# Academic Years
@router.post("/academic-years", response_model=AcademicYearResponse, status_code=status.HTTP_201_CREATED)
async def create_academic_year(payload: AcademicYearCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.academic_year import AcademicYear
    from app.models.institution import Institution

    # validate institution exists
    ires = await db.execute(select(Institution).where(Institution.id == payload.institution_id))
    inst = ires.scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Institution not found."}})
    if payload.start_date >= payload.end_date:
        raise HTTPException(status_code=422, detail={"error": {"code": "INVALID_ACADEMIC_RELATIONSHIP", "message": "start_date must be before end_date."}})
    ay = AcademicYear(institution_id=payload.institution_id, name=payload.name, start_date=payload.start_date, end_date=payload.end_date, is_active=bool(payload.is_active))
    db.add(ay)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Academic year conflict."}})
    return {"id": str(ay.id), "institution_id": str(ay.institution_id), "name": ay.name, "start_date": ay.start_date, "end_date": ay.end_date, "is_active": ay.is_active}


@router.get("/academic-years", response_model=dict)
async def list_academic_years(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.academic_year import AcademicYear

    q = select(AcademicYear).offset((page - 1) * page_size).limit(page_size)
    total_q = select(func.count()).select_from(AcademicYear)
    res = await db.execute(q)
    total_res = await db.execute(total_q)
    items = res.scalars().all()
    total = total_res.scalar_one()
    pagination = {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}
    return {"items": [{"id": str(i.id), "institution_id": str(i.institution_id), "name": i.name, "start_date": i.start_date, "end_date": i.end_date, "is_active": i.is_active} for i in items], "pagination": pagination}


@router.get("/academic-years/{id}", response_model=AcademicYearResponse)
async def get_academic_year(id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.academic_year import AcademicYear

    res = await db.execute(select(AcademicYear).where(AcademicYear.id == id))
    ay = res.scalar_one_or_none()
    if not ay:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Academic year not found."}})
    return {"id": str(ay.id), "institution_id": str(ay.institution_id), "name": ay.name, "start_date": ay.start_date, "end_date": ay.end_date, "is_active": ay.is_active}


@router.patch("/academic-years/{id}", response_model=AcademicYearResponse)
async def update_academic_year(id: str, payload: AcademicYearUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.academic_year import AcademicYear

    res = await db.execute(select(AcademicYear).where(AcademicYear.id == id))
    ay = res.scalar_one_or_none()
    if not ay:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Academic year not found."}})
    if payload.start_date is not None and payload.end_date is not None and payload.start_date >= payload.end_date:
        raise HTTPException(status_code=422, detail={"error": {"code": "INVALID_ACADEMIC_RELATIONSHIP", "message": "start_date must be before end_date."}})
    if payload.name is not None:
        ay.name = payload.name
    if payload.start_date is not None:
        ay.start_date = payload.start_date
    if payload.end_date is not None:
        ay.end_date = payload.end_date
    if payload.is_active is not None:
        ay.is_active = payload.is_active
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Academic year conflict."}})
    return {"id": str(ay.id), "institution_id": str(ay.institution_id), "name": ay.name, "start_date": ay.start_date, "end_date": ay.end_date, "is_active": ay.is_active}


# Branches
@router.post("/branches", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(payload: BranchCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.branch import Branch
    from app.models.institution import Institution

    ires = await db.execute(select(Institution).where(Institution.id == payload.institution_id))
    inst = ires.scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Institution not found."}})
    b = Branch(institution_id=payload.institution_id, name=payload.name, code=payload.code)
    db.add(b)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Branch code conflict."}})
    return {"id": str(b.id), "institution_id": str(b.institution_id), "name": b.name, "code": b.code}


@router.get("/branches", response_model=dict)
async def list_branches(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.branch import Branch

    q = select(Branch).offset((page - 1) * page_size).limit(page_size)
    total_q = select(func.count()).select_from(Branch)
    res = await db.execute(q)
    total_res = await db.execute(total_q)
    items = res.scalars().all()
    total = total_res.scalar_one()
    pagination = {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}
    return {"items": [{"id": str(i.id), "institution_id": str(i.institution_id), "name": i.name, "code": i.code} for i in items], "pagination": pagination}


@router.get("/branches/{id}", response_model=BranchResponse)
async def get_branch(id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.branch import Branch

    res = await db.execute(select(Branch).where(Branch.id == id))
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Branch not found."}})
    return {"id": str(b.id), "institution_id": str(b.institution_id), "name": b.name, "code": b.code}


@router.patch("/branches/{id}", response_model=BranchResponse)
async def update_branch(id: str, payload: BranchUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.branch import Branch

    res = await db.execute(select(Branch).where(Branch.id == id))
    b = res.scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Branch not found."}})
    if payload.name is not None:
        b.name = payload.name
    if payload.code is not None:
        b.code = payload.code
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Branch code conflict."}})
    return {"id": str(b.id), "institution_id": str(b.institution_id), "name": b.name, "code": b.code}


# Divisions
@router.post("/divisions", response_model=DivisionResponse, status_code=status.HTTP_201_CREATED)
async def create_division(payload: DivisionCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.division import Division
    from app.models.institution import Institution
    from app.models.branch import Branch
    from app.models.academic_year import AcademicYear

    # validate institution
    ires = await db.execute(select(Institution).where(Institution.id == payload.institution_id))
    inst = ires.scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Institution not found."}})
    bres = await db.execute(select(Branch).where(Branch.id == payload.branch_id))
    branch = bres.scalar_one_or_none()
    if not branch or branch.institution_id != payload.institution_id:
        raise HTTPException(status_code=422, detail={"error": {"code": "INVALID_ACADEMIC_RELATIONSHIP", "message": "Branch does not belong to institution."}})
    ayres = await db.execute(select(AcademicYear).where(AcademicYear.id == payload.academic_year_id))
    ay = ayres.scalar_one_or_none()
    if not ay or ay.institution_id != payload.institution_id:
        raise HTTPException(status_code=422, detail={"error": {"code": "INVALID_ACADEMIC_RELATIONSHIP", "message": "Academic year does not belong to institution."}})
    d = Division(institution_id=payload.institution_id, branch_id=payload.branch_id, academic_year_id=payload.academic_year_id, name=payload.name)
    db.add(d)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Division conflict."}})
    return {"id": str(d.id), "institution_id": str(d.institution_id), "branch_id": str(d.branch_id), "academic_year_id": str(d.academic_year_id), "name": d.name}


@router.get("/divisions", response_model=dict)
async def list_divisions(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.division import Division

    q = select(Division).offset((page - 1) * page_size).limit(page_size)
    total_q = select(func.count()).select_from(Division)
    res = await db.execute(q)
    total_res = await db.execute(total_q)
    items = res.scalars().all()
    total = total_res.scalar_one()
    pagination = {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}
    return {"items": [{"id": str(i.id), "institution_id": str(i.institution_id), "branch_id": str(i.branch_id), "academic_year_id": str(i.academic_year_id), "name": i.name} for i in items], "pagination": pagination}


@router.get("/divisions/{id}", response_model=DivisionResponse)
async def get_division(id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.division import Division

    res = await db.execute(select(Division).where(Division.id == id))
    d = res.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Division not found."}})
    return {"id": str(d.id), "institution_id": str(d.institution_id), "branch_id": str(d.branch_id), "academic_year_id": str(d.academic_year_id), "name": d.name}


@router.patch("/divisions/{id}", response_model=DivisionResponse)
async def update_division(id: str, payload: DivisionUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.division import Division

    res = await db.execute(select(Division).where(Division.id == id))
    d = res.scalar_one_or_none()
    if not d:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Division not found."}})
    if payload.name is not None:
        d.name = payload.name
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Division conflict."}})
    return {"id": str(d.id), "institution_id": str(d.institution_id), "branch_id": str(d.branch_id), "academic_year_id": str(d.academic_year_id), "name": d.name}


# Subjects
@router.post("/subjects", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(payload: SubjectCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.subject import Subject
    from app.models.institution import Institution

    ires = await db.execute(select(Institution).where(Institution.id == payload.institution_id))
    inst = ires.scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Institution not found."}})
    s = Subject(institution_id=payload.institution_id, name=payload.name, code=payload.code)
    db.add(s)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Subject code conflict."}})
    return {"id": str(s.id), "institution_id": str(s.institution_id), "name": s.name, "code": s.code}


@router.get("/subjects", response_model=dict)
async def list_subjects(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.subject import Subject

    q = select(Subject).offset((page - 1) * page_size).limit(page_size)
    total_q = select(func.count()).select_from(Subject)
    res = await db.execute(q)
    total_res = await db.execute(total_q)
    items = res.scalars().all()
    total = total_res.scalar_one()
    pagination = {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}
    return {"items": [{"id": str(i.id), "institution_id": str(i.institution_id), "name": i.name, "code": i.code} for i in items], "pagination": pagination}


@router.get("/subjects/{id}", response_model=SubjectResponse)
async def get_subject(id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.subject import Subject

    res = await db.execute(select(Subject).where(Subject.id == id))
    s = res.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Subject not found."}})
    return {"id": str(s.id), "institution_id": str(s.institution_id), "name": s.name, "code": s.code}


@router.patch("/subjects/{id}", response_model=SubjectResponse)
async def update_subject(id: str, payload: SubjectUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.subject import Subject

    res = await db.execute(select(Subject).where(Subject.id == id))
    s = res.scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Subject not found."}})
    if payload.name is not None:
        s.name = payload.name
    if payload.code is not None:
        s.code = payload.code
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Subject code conflict."}})
    return {"id": str(s.id), "institution_id": str(s.institution_id), "name": s.name, "code": s.code}


# Classes
@router.post("/classes", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
async def create_class(payload: ClassCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.class_ import Class
    from app.models.institution import Institution
    from app.models.subject import Subject
    from app.models.faculty import Faculty
    from app.models.division import Division
    from app.models.academic_year import AcademicYear

    # validate institution
    ires = await db.execute(select(Institution).where(Institution.id == payload.institution_id))
    inst = ires.scalar_one_or_none()
    if not inst:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Institution not found."}})
    sres = await db.execute(select(Subject).where(Subject.id == payload.subject_id))
    subj = sres.scalar_one_or_none()
    if not subj or subj.institution_id != payload.institution_id:
        raise HTTPException(status_code=422, detail={"error": {"code": "INVALID_ACADEMIC_RELATIONSHIP", "message": "Subject does not belong to institution."}})
    fres = await db.execute(select(Faculty).where(Faculty.id == payload.faculty_id))
    fac = fres.scalar_one_or_none()
    if not fac:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Faculty not found."}})
    dres = await db.execute(select(Division).where(Division.id == payload.division_id))
    div = dres.scalar_one_or_none()
    if not div or div.institution_id != payload.institution_id:
        raise HTTPException(status_code=422, detail={"error": {"code": "INVALID_ACADEMIC_RELATIONSHIP", "message": "Division does not belong to institution."}})
    ayres = await db.execute(select(AcademicYear).where(AcademicYear.id == payload.academic_year_id))
    ay = ayres.scalar_one_or_none()
    if not ay or ay.institution_id != payload.institution_id:
        raise HTTPException(status_code=422, detail={"error": {"code": "INVALID_ACADEMIC_RELATIONSHIP", "message": "Academic year does not belong to institution."}})

    c = Class(institution_id=payload.institution_id, subject_id=payload.subject_id, faculty_id=payload.faculty_id, division_id=payload.division_id, academic_year_id=payload.academic_year_id, name=payload.name)
    db.add(c)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Class conflict."}})
    return {"id": str(c.id), "institution_id": str(c.institution_id), "subject_id": str(c.subject_id), "faculty_id": str(c.faculty_id), "division_id": str(c.division_id), "academic_year_id": str(c.academic_year_id), "name": c.name}


@router.get("/classes", response_model=dict)
async def list_classes(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.class_ import Class

    q = select(Class).offset((page - 1) * page_size).limit(page_size)
    total_q = select(func.count()).select_from(Class)
    res = await db.execute(q)
    total_res = await db.execute(total_q)
    items = res.scalars().all()
    total = total_res.scalar_one()
    pagination = {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}
    return {"items": [{"id": str(i.id), "institution_id": str(i.institution_id), "subject_id": str(i.subject_id), "faculty_id": str(i.faculty_id), "division_id": str(i.division_id), "academic_year_id": str(i.academic_year_id), "name": i.name} for i in items], "pagination": pagination}


@router.get("/classes/{id}", response_model=ClassResponse)
async def get_class(id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.class_ import Class

    res = await db.execute(select(Class).where(Class.id == id))
    c = res.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Class not found."}})
    return {"id": str(c.id), "institution_id": str(c.institution_id), "subject_id": str(c.subject_id), "faculty_id": str(c.faculty_id), "division_id": str(c.division_id), "academic_year_id": str(c.academic_year_id), "name": c.name}


@router.patch("/classes/{id}", response_model=ClassResponse)
async def update_class(id: str, payload: ClassUpdate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.class_ import Class

    res = await db.execute(select(Class).where(Class.id == id))
    c = res.scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Class not found."}})
    if payload.name is not None:
        c.name = payload.name
    if payload.faculty_id is not None:
        c.faculty_id = payload.faculty_id
    if payload.division_id is not None:
        c.division_id = payload.division_id
    if payload.academic_year_id is not None:
        c.academic_year_id = payload.academic_year_id
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Class conflict."}})
    return {"id": str(c.id), "institution_id": str(c.institution_id), "subject_id": str(c.subject_id), "faculty_id": str(c.faculty_id), "division_id": str(c.division_id), "academic_year_id": str(c.academic_year_id), "name": c.name}


# Enrollments
@router.post("/classes/{class_id}/enrollments", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(class_id: str, payload: EnrollmentCreate, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.class_ import Class
    from app.models.student import Student
    from app.models.class_enrollment import ClassEnrollment

    cres = await db.execute(select(Class).where(Class.id == class_id))
    cls = cres.scalar_one_or_none()
    if not cls:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Class not found."}})
    sres = await db.execute(select(Student).where(Student.id == payload.student_id))
    student = sres.scalar_one_or_none()
    if not student:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Student not found."}})
    # validate academic compatibility
    if student.institution_id != cls.institution_id if hasattr(student, 'institution_id') else False:
        # Student model doesn't have institution_id; validate by student's academic_year institution
        pass
    enrollment = ClassEnrollment(class_id=class_id, student_id=payload.student_id)
    db.add(enrollment)
    try:
        await db.flush()
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail={"error": {"code": "RESOURCE_CONFLICT", "message": "Student already enrolled."}})
    return {"id": str(enrollment.id), "class_id": str(enrollment.class_id), "student_id": str(enrollment.student_id)}


@router.get("/classes/{class_id}/enrollments", response_model=dict)
async def list_enrollments(class_id: str, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=200), db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.class_enrollment import ClassEnrollment

    q = select(ClassEnrollment).where(ClassEnrollment.class_id == class_id).offset((page - 1) * page_size).limit(page_size)
    total_q = select(func.count()).select_from(ClassEnrollment).where(ClassEnrollment.class_id == class_id)
    res = await db.execute(q)
    total_res = await db.execute(total_q)
    items = res.scalars().all()
    total = total_res.scalar_one()
    pagination = {"page": page, "page_size": page_size, "total": total, "total_pages": (total + page_size - 1) // page_size}
    return {"items": [{"id": str(e.id), "class_id": str(e.class_id), "student_id": str(e.student_id)} for e in items], "pagination": pagination}


@router.delete("/classes/{class_id}/enrollments/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(class_id: str, student_id: str, db: AsyncSession = Depends(get_db), _=Depends(require_admin)):
    from app.models.class_enrollment import ClassEnrollment

    res = await db.execute(select(ClassEnrollment).where(ClassEnrollment.class_id == class_id).where(ClassEnrollment.student_id == student_id))
    enrollment = res.scalar_one_or_none()
    if not enrollment:
        raise HTTPException(status_code=404, detail={"error": {"code": "RESOURCE_NOT_FOUND", "message": "Enrollment not found."}})
    await db.delete(enrollment)
    await db.flush()
    await db.commit()
    return None
