from enum import StrEnum


class UserRole(StrEnum):
    STUDENT = "STUDENT"
    FACULTY = "FACULTY"
    ADMIN = "ADMIN"


class SessionStatus(StrEnum):
    CREATED = "CREATED"
    ACTIVE = "ACTIVE"
    ENDED = "ENDED"


class AttendanceStatus(StrEnum):
    PRESENT = "PRESENT"


class VerificationStatus(StrEnum):
    CREATED = "CREATED"
    LOCATION_VERIFIED = "LOCATION_VERIFIED"
    FACE_VERIFIED = "FACE_VERIFIED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    EXPIRED = "EXPIRED"
