from __future__ import annotations

from pydantic import BaseModel, EmailStr
from typing import List, Optional


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    profile_image_url: Optional[str] = None


class BranchResponse(BaseModel):
    id: str
    name: str
    code: str


class DivisionResponse(BaseModel):
    id: str
    name: str


class AcademicYearResponse(BaseModel):
    id: str
    name: str


class StudentResponse(BaseModel):
    id: str
    user: UserResponse
    prn: str
    roll_number: str
    branch: BranchResponse
    division: DivisionResponse
    academic_year: AcademicYearResponse


class SubjectResponse(BaseModel):
    id: str
    name: str
    code: str


class FacultyResponse(BaseModel):
    id: str
    user: UserResponse
    employee_id: str
    department: str


class ClassResponse(BaseModel):
    id: str
    name: str
    subject: Optional[SubjectResponse]
    faculty: Optional[FacultyResponse]
    division: Optional[DivisionResponse]
    academic_year: Optional[AcademicYearResponse]


class PagedResponse(BaseModel):
    items: List
    pagination: Optional[dict] = None


class DashboardResponse(BaseModel):
    student: dict
    academic: dict
    classes: List[ClassResponse]
