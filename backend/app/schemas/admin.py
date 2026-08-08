from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


class Pagination(BaseModel):
    page: int = 1
    page_size: int = 20
    total: Optional[int]
    total_pages: Optional[int]


class InstitutionCreate(BaseModel):
    name: str
    code: str


class InstitutionUpdate(BaseModel):
    name: Optional[str]
    code: Optional[str]


class InstitutionResponse(BaseModel):
    id: str
    name: str
    code: str


class AcademicYearCreate(BaseModel):
    institution_id: str
    name: str
    start_date: date
    end_date: date
    is_active: Optional[bool] = False


class AcademicYearUpdate(BaseModel):
    name: Optional[str]
    start_date: Optional[date]
    end_date: Optional[date]
    is_active: Optional[bool]


class AcademicYearResponse(BaseModel):
    id: str
    institution_id: str
    name: str
    start_date: date
    end_date: date
    is_active: bool


class BranchCreate(BaseModel):
    institution_id: str
    name: str
    code: str


class BranchUpdate(BaseModel):
    name: Optional[str]
    code: Optional[str]


class BranchResponse(BaseModel):
    id: str
    institution_id: str
    name: str
    code: str


class DivisionCreate(BaseModel):
    institution_id: str
    branch_id: str
    academic_year_id: str
    name: str


class DivisionUpdate(BaseModel):
    name: Optional[str]


class DivisionResponse(BaseModel):
    id: str
    institution_id: str
    branch_id: str
    academic_year_id: str
    name: str


class SubjectCreate(BaseModel):
    institution_id: str
    name: str
    code: str


class SubjectUpdate(BaseModel):
    name: Optional[str]
    code: Optional[str]


class SubjectResponse(BaseModel):
    id: str
    institution_id: str
    name: str
    code: str


class ClassCreate(BaseModel):
    institution_id: str
    subject_id: str
    faculty_id: str
    division_id: str
    academic_year_id: str
    name: str


class ClassUpdate(BaseModel):
    name: Optional[str]
    faculty_id: Optional[str]
    division_id: Optional[str]
    academic_year_id: Optional[str]


class ClassResponse(BaseModel):
    id: str
    institution_id: str
    subject_id: str
    faculty_id: str
    division_id: str
    academic_year_id: str
    name: str


class EnrollmentCreate(BaseModel):
    student_id: str


class EnrollmentResponse(BaseModel):
    id: str
    class_id: str
    student_id: str


class PagedItems(BaseModel):
    items: List
    pagination: Pagination
