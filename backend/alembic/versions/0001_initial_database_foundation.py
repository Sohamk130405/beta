"""initial database foundation

Revision ID: 0001_initial_database_foundation
Revises:
Create Date: 2026-08-08 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

from alembic import op

revision: str = "0001_initial_database_foundation"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

user_role = postgresql.ENUM(
    "STUDENT",
    "FACULTY",
    "ADMIN",
    name="user_role",
    create_type=False,
)
session_status = postgresql.ENUM(
    "CREATED",
    "ACTIVE",
    "ENDED",
    name="session_status",
    create_type=False,
)
attendance_status = postgresql.ENUM(
    "PRESENT",
    name="attendance_status",
    create_type=False,
)
verification_status = postgresql.ENUM(
    "CREATED",
    "LOCATION_VERIFIED",
    "FACE_VERIFIED",
    "COMPLETED",
    "FAILED",
    "EXPIRED",
    name="verification_status",
    create_type=False,
)


def upgrade() -> None:
    """Upgrade schema."""
    bind = op.get_bind()
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    user_role.create(bind, checkfirst=True)
    session_status.create(bind, checkfirst=True)
    attendance_status.create(bind, checkfirst=True)
    verification_status.create(bind, checkfirst=True)

    op.create_table(
        "institutions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_institutions_code", "institutions", ["code"])

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("google_id", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("profile_image_url", sa.Text(), nullable=True),
        sa.Column("role", user_role, nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("google_id"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_google_id", "users", ["google_id"])

    op.create_table(
        "academic_years",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("institution_id", "name", name="uq_academic_years_institution_name"),
    )
    op.create_index("ix_academic_years_institution_id", "academic_years", ["institution_id"])

    op.create_table(
        "branches",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("institution_id", "code", name="uq_branches_institution_code"),
    )
    op.create_index("ix_branches_institution_id", "branches", ["institution_id"])

    op.create_table(
        "faculty",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("employee_id", sa.String(length=64), nullable=False),
        sa.Column("department", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("employee_id", name="uq_faculty_employee_id"),
        sa.UniqueConstraint("user_id", name="uq_faculty_user_id"),
    )
    op.create_index("ix_faculty_employee_id", "faculty", ["employee_id"])
    op.create_index("ix_faculty_user_id", "faculty", ["user_id"])

    op.create_table(
        "subjects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("institution_id", "code", name="uq_subjects_institution_code"),
    )
    op.create_index("ix_subjects_institution_id", "subjects", ["institution_id"])

    op.create_table(
        "divisions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("academic_year_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["academic_year_id"], ["academic_years.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "branch_id",
            "academic_year_id",
            "name",
            name="uq_divisions_branch_academic_year_name",
        ),
    )
    op.create_index("ix_divisions_academic_year_id", "divisions", ["academic_year_id"])
    op.create_index("ix_divisions_branch_id", "divisions", ["branch_id"])
    op.create_index("ix_divisions_institution_id", "divisions", ["institution_id"])

    op.create_table(
        "students",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("prn", sa.String(length=64), nullable=False),
        sa.Column("roll_number", sa.String(length=64), nullable=False),
        sa.Column("branch_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("division_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("academic_year_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["academic_year_id"], ["academic_years.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["branch_id"], ["branches.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["division_id"], ["divisions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("prn", name="uq_students_prn"),
        sa.UniqueConstraint("user_id", name="uq_students_user_id"),
    )
    op.create_index("ix_students_academic_year_id", "students", ["academic_year_id"])
    op.create_index("ix_students_branch_id", "students", ["branch_id"])
    op.create_index("ix_students_division_id", "students", ["division_id"])
    op.create_index("ix_students_prn", "students", ["prn"])
    op.create_index("ix_students_user_id", "students", ["user_id"])

    op.create_table(
        "classes",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("institution_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("faculty_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("division_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("academic_year_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["academic_year_id"], ["academic_years.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["division_id"], ["divisions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculty.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["institution_id"], ["institutions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_classes_academic_year_id", "classes", ["academic_year_id"])
    op.create_index("ix_classes_division_id", "classes", ["division_id"])
    op.create_index("ix_classes_faculty_id", "classes", ["faculty_id"])
    op.create_index("ix_classes_institution_id", "classes", ["institution_id"])
    op.create_index("ix_classes_subject_id", "classes", ["subject_id"])

    op.create_table(
        "class_enrollments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "class_id",
            "student_id",
            name="uq_class_enrollments_class_student",
        ),
    )
    op.create_index("ix_class_enrollments_class_id", "class_enrollments", ["class_id"])
    op.create_index("ix_class_enrollments_student_id", "class_enrollments", ["student_id"])

    op.create_table(
        "face_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("embedding", Vector(), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("model_version", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_id", name="uq_face_profiles_student_id"),
    )
    op.create_index("ix_face_profiles_student_id", "face_profiles", ["student_id"])

    op.create_table(
        "attendance_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("class_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("faculty_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("radius_meters", sa.Numeric(10, 2), nullable=False),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", session_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["class_id"], ["classes.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["faculty_id"], ["faculty.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attendance_sessions_class_id", "attendance_sessions", ["class_id"])
    op.create_index(
        "ix_attendance_sessions_class_status",
        "attendance_sessions",
        ["class_id", "status"],
    )
    op.create_index("ix_attendance_sessions_ends_at", "attendance_sessions", ["ends_at"])
    op.create_index("ix_attendance_sessions_faculty_id", "attendance_sessions", ["faculty_id"])
    op.create_index("ix_attendance_sessions_starts_at", "attendance_sessions", ["starts_at"])
    op.create_index("ix_attendance_sessions_status", "attendance_sessions", ["status"])
    op.create_index(
        "ix_attendance_sessions_time_status",
        "attendance_sessions",
        ["starts_at", "ends_at", "status"],
    )

    op.create_table(
        "attendance",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("marked_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=False),
        sa.Column("location_accuracy", sa.Numeric(10, 2), nullable=False),
        sa.Column("distance_meters", sa.Numeric(10, 2), nullable=False),
        sa.Column("face_verified", sa.Boolean(), nullable=False),
        sa.Column("face_score", sa.Numeric(8, 6), nullable=True),
        sa.Column("status", attendance_status, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["attendance_sessions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "student_id", name="uq_attendance_session_student"),
    )
    op.create_index("ix_attendance_marked_at", "attendance", ["marked_at"])
    op.create_index("ix_attendance_session_id", "attendance", ["session_id"])
    op.create_index("ix_attendance_student_id", "attendance", ["student_id"])
    op.create_index("ix_attendance_student_marked_at", "attendance", ["student_id", "marked_at"])

    op.create_table(
        "verification_attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("student_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", verification_status, nullable=False),
        sa.Column("latitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("longitude", sa.Numeric(9, 6), nullable=True),
        sa.Column("accuracy", sa.Numeric(10, 2), nullable=True),
        sa.Column("distance_meters", sa.Numeric(10, 2), nullable=True),
        sa.Column("location_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("face_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("face_score", sa.Numeric(8, 6), nullable=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["attendance_sessions.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_verification_attempts_expires_at", "verification_attempts", ["expires_at"])
    op.create_index("ix_verification_attempts_session_id", "verification_attempts", ["session_id"])
    op.create_index("ix_verification_attempts_status", "verification_attempts", ["status"])
    op.create_index("ix_verification_attempts_student_id", "verification_attempts", ["student_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_verification_attempts_student_id", table_name="verification_attempts")
    op.drop_index("ix_verification_attempts_status", table_name="verification_attempts")
    op.drop_index("ix_verification_attempts_session_id", table_name="verification_attempts")
    op.drop_index("ix_verification_attempts_expires_at", table_name="verification_attempts")
    op.drop_table("verification_attempts")

    op.drop_index("ix_attendance_student_marked_at", table_name="attendance")
    op.drop_index("ix_attendance_student_id", table_name="attendance")
    op.drop_index("ix_attendance_session_id", table_name="attendance")
    op.drop_index("ix_attendance_marked_at", table_name="attendance")
    op.drop_table("attendance")

    op.drop_index("ix_attendance_sessions_time_status", table_name="attendance_sessions")
    op.drop_index("ix_attendance_sessions_status", table_name="attendance_sessions")
    op.drop_index("ix_attendance_sessions_starts_at", table_name="attendance_sessions")
    op.drop_index("ix_attendance_sessions_faculty_id", table_name="attendance_sessions")
    op.drop_index("ix_attendance_sessions_ends_at", table_name="attendance_sessions")
    op.drop_index("ix_attendance_sessions_class_status", table_name="attendance_sessions")
    op.drop_index("ix_attendance_sessions_class_id", table_name="attendance_sessions")
    op.drop_table("attendance_sessions")

    op.drop_index("ix_face_profiles_student_id", table_name="face_profiles")
    op.drop_table("face_profiles")

    op.drop_index("ix_class_enrollments_student_id", table_name="class_enrollments")
    op.drop_index("ix_class_enrollments_class_id", table_name="class_enrollments")
    op.drop_table("class_enrollments")

    op.drop_index("ix_classes_subject_id", table_name="classes")
    op.drop_index("ix_classes_institution_id", table_name="classes")
    op.drop_index("ix_classes_faculty_id", table_name="classes")
    op.drop_index("ix_classes_division_id", table_name="classes")
    op.drop_index("ix_classes_academic_year_id", table_name="classes")
    op.drop_table("classes")

    op.drop_index("ix_students_user_id", table_name="students")
    op.drop_index("ix_students_prn", table_name="students")
    op.drop_index("ix_students_division_id", table_name="students")
    op.drop_index("ix_students_branch_id", table_name="students")
    op.drop_index("ix_students_academic_year_id", table_name="students")
    op.drop_table("students")

    op.drop_index("ix_divisions_institution_id", table_name="divisions")
    op.drop_index("ix_divisions_branch_id", table_name="divisions")
    op.drop_index("ix_divisions_academic_year_id", table_name="divisions")
    op.drop_table("divisions")

    op.drop_index("ix_subjects_institution_id", table_name="subjects")
    op.drop_table("subjects")

    op.drop_index("ix_faculty_user_id", table_name="faculty")
    op.drop_index("ix_faculty_employee_id", table_name="faculty")
    op.drop_table("faculty")

    op.drop_index("ix_branches_institution_id", table_name="branches")
    op.drop_table("branches")

    op.drop_index("ix_academic_years_institution_id", table_name="academic_years")
    op.drop_table("academic_years")

    op.drop_index("ix_users_google_id", table_name="users")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_institutions_code", table_name="institutions")
    op.drop_table("institutions")

    verification_status.drop(op.get_bind(), checkfirst=True)
    attendance_status.drop(op.get_bind(), checkfirst=True)
    session_status.drop(op.get_bind(), checkfirst=True)
    user_role.drop(op.get_bind(), checkfirst=True)
    op.execute("DROP EXTENSION IF EXISTS vector")
