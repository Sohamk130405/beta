# GeoAttend — Codex Agent Instructions

## 1. Purpose

You are working on **GeoAttend**, a production-oriented geolocation and facial-verification attendance application.

GeoAttend allows students to mark attendance using:

* Google authentication
* Class/session eligibility
* Geolocation verification
* Facial verification
* Server-side validation

Faculty can:

* Create attendance sessions
* Monitor live attendance
* View attendance history
* Manage authorized classes

Administrators can manage:

* Students
* Faculty
* Academic structure
* Classes
* Attendance data
* Reports

---

# 2. Mandatory Context

Before making architectural or cross-cutting changes, read:

```text
docs/PRODUCT.md
docs/ARCHITECTURE.md
docs/DATABASE.md
docs/UI.md
docs/SECURITY.md
docs/API.md
```

These documents define the intended system.

Do not contradict them without first identifying the conflict and updating the relevant documentation.

---

# 3. Source of Truth

Use the following hierarchy:

```text
Product requirements
        ↓
Architecture
        ↓
Security
        ↓
Database
        ↓
API
        ↓
Implementation
        ↓
UI details
```

If implementation conflicts with documentation:

1. Stop.
2. Determine whether the documentation is outdated.
3. Update the relevant documentation if the new design is intentional.
4. Then implement the change.

Do not silently create a second architecture.

---

# 4. Technology Stack

## Frontend

```text
Next.js
TypeScript
Tailwind CSS
TanStack Query
Zustand
```

## Backend

```text
Python
FastAPI
Pydantic
SQLAlchemy 2.x
asyncpg
Alembic
```

## Database

```text
PostgreSQL
pgvector where required
```

## Authentication

```text
Google OAuth
```

## Security / Rate Limiting

```text
Arcjet
```

## Infrastructure

The exact deployment platform may change.

Do not tightly couple application logic to a deployment provider.

---

# 5. Repository Architecture

The repository should remain clearly separated between frontend and backend.

Recommended structure:

```text
geoattend/
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── features/
│   ├── hooks/
│   ├── lib/
│   ├── stores/
│   ├── types/
│   └── ...
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── db/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   └── main.py
│   │
│   ├── migrations/
│   └── tests/
│
├── docs/
│
├── .env.example
├── .gitignore
├── AGENTS.md
└── README.md
```

The exact folder names may evolve, but responsibilities must remain separated.

---

# 6. General Engineering Principles

Prioritize:

1. Correctness
2. Security
3. Maintainability
4. Simplicity
5. Testability
6. Performance

Do not optimize prematurely.

Do not introduce abstractions without a real reason.

Do not add libraries simply because they are popular.

---

# 7. Before Writing Code

Before implementing a non-trivial feature:

1. Understand the existing architecture.
2. Identify affected files.
3. Read relevant documentation.
4. Check existing implementations for reusable patterns.
5. Determine whether the API/database contract changes.
6. Implement the smallest coherent change.
7. Run appropriate tests/checks.

Do not immediately rewrite large portions of the codebase.

---

# 8. Ask Before Major Architectural Changes

Do not independently make major changes such as:

* Replacing FastAPI
* Replacing PostgreSQL
* Replacing Next.js
* Replacing TanStack Query
* Replacing Zustand
* Replacing OAuth
* Introducing another database
* Introducing microservices
* Introducing Redis
* Introducing Kafka
* Introducing WebSockets
* Replacing the face-recognition architecture

unless explicitly requested or clearly required.

If a major architectural change appears necessary, explain the tradeoff first.

---

# 9. Backend Architecture

FastAPI should use clear layers.

Recommended:

```text
Router
   ↓
Service
   ↓
Repository
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

Conceptually:

```text
API layer
    ↓
Business logic
    ↓
Data access
    ↓
Database
```

---

# 10. Router Responsibilities

FastAPI routers should handle:

* Request parsing
* Authentication dependencies
* Authorization dependencies
* Calling services
* Response serialization
* HTTP-specific behavior

Routers should not contain large business workflows.

Avoid:

```python id="r1m1xk"
@router.post(...)
async def mark_attendance(...):
    # 200 lines of business logic
```

Prefer:

```python id="t5u2s8"
@router.post(...)
async def mark_attendance(...):
    return await attendance_service.complete_verification(...)
```

---

# 11. Service Layer

Services contain domain/business logic.

Examples:

```text
AttendanceService
VerificationService
SessionService
StudentService
FacultyService
FaceService
```

Business rules should live here rather than inside routers.

---

# 12. Repository Layer

Repositories handle database access.

Example:

```text
StudentRepository
SessionRepository
AttendanceRepository
ClassRepository
FaceProfileRepository
```

Repositories should not contain UI or HTTP logic.

---

# 13. Database Models

SQLAlchemy models represent database entities.

Do not create database models directly from API request objects.

Separate:

```text
SQLAlchemy model
        ≠
Pydantic request schema
        ≠
Pydantic response schema
```

This separation is intentional.

---

# 14. Pydantic Schemas

Use Pydantic schemas for:

* Request validation
* Response serialization
* API contracts

Example:

```text
schemas/
├── auth.py
├── student.py
├── faculty.py
├── session.py
├── attendance.py
└── verification.py
```

Schemas should remain focused.

Avoid giant `schemas.py` files.

---

# 15. Database Migrations

All schema changes must use Alembic.

Never manually modify production database schemas as part of normal development.

Workflow:

```text
Modify SQLAlchemy model
        ↓
Create Alembic migration
        ↓
Review migration
        ↓
Run migration
        ↓
Test
```

---

# 16. Migration Safety

Before creating a migration:

* Understand existing data.
* Consider nullable/non-nullable transitions.
* Consider existing foreign keys.
* Consider indexes.
* Consider production migration safety.

Do not casually drop columns/tables.

Destructive migrations require explicit consideration.

---

# 17. PostgreSQL

Use PostgreSQL features where they provide clear value.

Examples:

* UUID
* Constraints
* Transactions
* Indexes
* JSONB when justified
* pgvector for embeddings

Do not move data into another storage system merely because PostgreSQL can technically be supplemented.

---

# 18. Database Integrity

Critical constraints should be enforced at the database level.

Example:

```text
UNIQUE(session_id, student_id)
```

for attendance.

Application checks are not sufficient by themselves.

---

# 19. Transactions

Use database transactions for multi-step operations that must succeed or fail atomically.

Attendance completion is a critical example.

Conceptually:

```text
BEGIN
   validate
   create attendance
COMMIT
```

If something fails:

```text
ROLLBACK
```

---

# 20. Attendance Must Be Backend-Controlled

Never allow the frontend to decide:

```text
is_present
location_verified
face_verified
distance
attendance_status
```

The frontend may provide:

```text
latitude
longitude
accuracy
face image
session ID
```

FastAPI performs verification.

---

# 21. Attendance Verification State Machine

Attendance verification follows:

```text
CREATED
   ↓
LOCATION_VERIFIED
   ↓
FACE_VERIFIED
   ↓
COMPLETED
```

Possible failure states:

```text
FAILED
EXPIRED
```

The client must never directly set the verification state.

---

# 22. Verification Context

Verification contexts must be:

* Short-lived
* User-bound
* Session-bound
* Server-controlled

A verification context for:

```text
Student A
Session X
```

must never be usable for:

```text
Student B
Session Y
```

---

# 23. Face Recognition

Treat face recognition as a security-sensitive subsystem.

The initial architecture should use:

```text
Authenticated Student
        ↓
Registered Face Profile
        ↓
Live Face
        ↓
1:1 Verification
```

Do not implement unrestricted 1:N identification unless explicitly required.

---

# 24. Face Embeddings

Do not expose face embeddings through normal API responses.

Never send:

```json id="v5n6zj"
{
  "embedding": [...]
}
```

to the frontend.

Embeddings are sensitive biometric representations.

---

# 25. Face Images

If raw images are temporarily uploaded:

* Validate them.
* Process them.
* Avoid persistent storage unless explicitly required.
* Never log them.
* Never expose them through public URLs unnecessarily.

---

# 26. Face Model Loading

Do not initialize expensive face models for every request if the selected implementation supports safe reuse.

Prefer application-level initialization:

```text
Application startup
       ↓
Load model
       ↓
Reuse
```

while respecting the concurrency/thread-safety characteristics of the chosen library.

---

# 27. Liveness Detection

Liveness detection is a future security enhancement unless explicitly included in the current implementation phase.

Do not fake liveness detection.

Do not label ordinary face matching as "anti-spoofing."

If liveness is not implemented:

```text
face_verified = face verification
```

not:

```text
anti_spoof_verified = true
```

---

# 28. Geolocation

Never trust client-provided:

```text
distance
is_within_radius
location_verified
```

The client provides coordinates.

The backend calculates distance.

Conceptually:

```text
Student coordinates
        +
Session coordinates
        ↓
Server-side distance calculation
        ↓
Radius validation
```

---

# 29. GPS Accuracy

Consider the reported GPS accuracy when deciding whether location evidence is sufficient.

Do not blindly accept:

```text
distance < radius
```

when the reported accuracy makes that measurement unreliable.

Exact thresholds belong in configuration and should be validated through testing.

---

# 30. Server Time

Never trust client time for attendance validity.

Use:

```text
server time
database time
```

where appropriate.

Store timestamps in UTC.

---

# 31. Authorization

Every protected operation requires:

```text
Authentication
      ↓
Role authorization
      ↓
Resource authorization
```

Example:

```text
FACULTY
   +
assigned to class
   ↓
allowed to create session
```

---

# 32. Object-Level Authorization

Never assume that knowing a UUID means a user can access it.

Always check ownership/relationship.

Example:

```text
GET /sessions/{session_id}
```

must verify whether the authenticated user is allowed to access that session.

---

# 33. Frontend Architecture

Next.js should be organized around features and domain concepts.

Recommended:

```text
frontend/
├── app/
├── components/
├── features/
│   ├── auth/
│   ├── attendance/
│   ├── students/
│   ├── faculty/
│   └── admin/
├── hooks/
├── lib/
├── stores/
├── types/
└── ...
```

Do not put the entire application inside generic `components/`.

---

# 34. Next.js App Router

Use the Next.js App Router.

Prefer:

```text
app/
```

with route groups/layouts where useful.

Use server components where they provide meaningful value.

Use client components only when client-side behavior is required.

---

# 35. Client Components

Use `"use client"` when required for:

* Browser APIs
* Camera
* Geolocation
* Zustand
* Interactive forms
* TanStack Query
* Client-side event handling

Do not mark entire route trees as client components unnecessarily.

---

# 36. TanStack Query

TanStack Query is the primary source of truth for server state.

Use it for:

* API data
* Attendance data
* Sessions
* Student profile
* Faculty data
* Reports

Do not duplicate server data into Zustand without a specific reason.

---

# 37. Zustand

Zustand is for client/application state.

Good candidates:

```text
UI preferences
Modal state
Verification UI state
Temporary client workflow state
Local interaction state
```

Do not use Zustand as a replacement for TanStack Query.

Avoid:

```text
API response
    ↓
Zustand
    ↓
components
```

when TanStack Query can manage the server state directly.

---

# 38. API Client

The frontend should have a centralized API client.

For example:

```text
lib/api/
```

or:

```text
lib/api-client.ts
```

The API client should handle:

* Base URL
* Request configuration
* Authentication behavior
* JSON parsing
* Error normalization

Do not scatter raw `fetch()` configuration throughout components.

---

# 39. API Types

Frontend types should correspond to API contracts.

For example:

```text
types/
├── auth.ts
├── student.ts
├── faculty.ts
├── attendance.ts
├── session.ts
└── verification.ts
```

Prefer generated types from OpenAPI if the project establishes a reliable generation workflow.

Do not manually duplicate large API schemas if they can safely be generated.

---

# 40. Error Handling

Frontend errors should use backend error codes.

Example:

```text
LOCATION_OUTSIDE_RADIUS
```

maps to appropriate UI:

```text
You're outside the attendance area.
```

Do not build frontend logic around fragile backend error message strings.

---

# 41. Loading States

Every important asynchronous operation needs a meaningful loading state.

Examples:

```text
Finding your location...
Preparing camera...
Verifying identity...
Loading attendance...
```

Avoid generic indefinite spinners when a meaningful state can be shown.

---

# 42. Attendance UI

Follow `docs/UI.md`.

The attendance flow should remain:

```text
Session
   ↓
Location
   ↓
Face
   ↓
Verification
   ↓
Success
```

Do not turn the flow into a large generic form.

---

# 43. Camera Implementation

Camera functionality must:

* Request permission only when required.
* Stop camera streams when leaving the verification screen.
* Handle denied permissions.
* Handle unavailable cameras.
* Handle mobile browser differences.
* Provide clear feedback.

Do not leave camera streams running after verification.

---

# 44. Geolocation Implementation

The frontend should:

1. Request location permission.
2. Obtain location.
3. Display meaningful state.
4. Submit coordinates and accuracy.
5. Let the backend determine validity.

The frontend should not independently declare attendance location valid.

---

# 45. Permissions UX

Before requesting camera/location permissions, explain why they are needed.

Example:

```text
Camera access is required to verify your identity.
```

and:

```text
Location access is required to confirm that you're at the class.
```

---

# 46. Tailwind CSS

Use Tailwind CSS consistently.

Prefer design tokens and reusable component styles.

Avoid excessive arbitrary values.

Bad:

```text
mt-[17px]
rounded-[13px]
text-[#123456]
```

when an existing design token is appropriate.

---

# 47. Component Design

Prefer domain-oriented components.

Good:

```text
AttendanceCard
SessionStatus
VerificationStep
LocationStatus
FaceCapture
AttendanceSummary
StudentAttendanceList
```

Avoid meaningless generic names:

```text
BlueCard
BigBox
CustomContainer2
```

---

# 48. Reusability

Do not abstract components prematurely.

Create reusable components when:

* They are used in multiple places.
* They represent a meaningful design primitive.
* Reuse improves consistency.
* Their API remains understandable.

Do not create a generic abstraction merely to reduce a few lines of JSX.

---

# 49. UI Consistency

Follow `docs/UI.md`.

Do not introduce random:

* colors
* border radii
* shadows
* typography
* spacing
* button styles

If a new pattern is needed repeatedly, add it to the design system.

---

# 50. Accessibility

Every interactive UI must consider:

* Keyboard navigation
* Focus states
* Semantic HTML
* Accessible labels
* Contrast
* Screen-reader announcements
* Non-color status indicators

Do not use color as the only indicator.

---

# 51. Responsive Design

The application must work on:

```text
Mobile
Tablet
Desktop
```

Student attendance is mobile-first.

Faculty and admin workflows can use denser desktop layouts.

---

# 52. Security Rules

Never:

* Commit secrets
* Log tokens
* Log face embeddings
* Log raw face images
* Trust client authorization
* Trust client distance calculations
* Trust client attendance status
* Expose database credentials
* Expose internal stack traces

---

# 53. Environment Variables

Never hardcode secrets.

Use environment variables.

Maintain:

```text
.env.example
```

with placeholder values.

Example:

```text
DATABASE_URL=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
ARCJET_KEY=
```

Actual variable names should match the implementation.

---

# 54. CORS

Production CORS must be restricted to the actual frontend origin.

Never casually configure:

```python
allow_origins=["*"]
```

for authenticated production APIs.

---

# 55. Rate Limiting

Arcjet should protect security-sensitive endpoints.

Especially:

```text
/auth/*
/students/me/face
/attendance/sessions/{id}/verification
/attendance/verifications/{id}/face
/attendance/verifications/{id}/complete
```

Exact configuration should be based on expected usage and testing.

---

# 56. Database Rules

Never bypass SQLAlchemy/Alembic conventions casually.

Use:

```text
SQLAlchemy models
Alembic migrations
Repositories
Transactions
```

Do not create ad-hoc SQL schema changes.

Raw SQL may be used when justified, but it must remain parameterized and reviewed.

---

# 57. Testing

Every meaningful backend feature should have tests.

Recommended backend layers:

```text
Unit tests
Service tests
API tests
Integration tests
```

Critical security workflows require integration tests.

---

# 58. Mandatory Attendance Tests

At minimum:

```text
Valid attendance
Duplicate attendance
Expired session
Student not enrolled
Outside radius
Poor GPS accuracy
Face not registered
Face verification failure
Unauthorized session
Unauthorized faculty
Verification expiration
Concurrent duplicate requests
```

---

# 59. Frontend Testing

Important frontend flows should be tested.

Examples:

```text
Login state
Student dashboard
Attendance flow
Location failure
Camera permission failure
Face verification failure
Attendance success
Faculty session creation
Live attendance
```

---

# 60. Type Safety

TypeScript strictness should remain enabled.

Do not solve type errors using:

```typescript
any
```

unless there is a documented reason.

Prefer:

```text
unknown
type guards
proper interfaces
generated API types
```

---

# 61. Python Type Safety

Use Python type hints throughout the backend.

Prefer:

```python
async def get_student(student_id: UUID) -> Student:
```

over untyped functions.

Use Pydantic for external data validation.

---

# 62. Async Programming

FastAPI endpoints should use async appropriately.

Database operations using async SQLAlchemy/asyncpg should remain non-blocking.

Do not place CPU-heavy face processing directly into the async event loop if the selected implementation blocks significantly.

If face processing becomes CPU-bound, evaluate:

* thread pool
* process pool
* worker architecture

before introducing complexity.

---

# 63. Performance

Do not optimize without evidence.

Priorities:

```text
Database query efficiency
API latency
Face processing latency
Frontend rendering
Network requests
```

Avoid unnecessary:

* N+1 queries
* duplicate API requests
* repeated face-model initialization
* full-cache invalidation

---

# 64. TanStack Query Rules

Use query keys consistently.

Example:

```text
["auth", "me"]

["student", "dashboard"]

["student", "attendance"]

["attendance", "session", sessionId]

["attendance", "session", sessionId, "students"]
```

Query key conventions should be centralized where practical.

---

# 65. Cache Invalidation

Invalidate only affected queries.

After attendance completion:

```text
student dashboard
attendance summary
attendance history
active sessions
```

After faculty ends a session:

```text
faculty dashboard
session details
session attendance
session list
```

Do not clear the entire query cache.

---

# 66. Optimistic Updates

Do not use optimistic updates for security-sensitive operations.

Especially:

```text
Attendance marking
Face verification
Location verification
Session creation
```

Wait for backend confirmation.

---

# 67. Git Practices

Keep commits focused.

Good:

```text
feat: add attendance session creation
feat: add student attendance verification
fix: prevent duplicate attendance
test: add attendance verification tests
```

Avoid giant commits containing unrelated changes.

---

# 68. Do Not Rewrite Working Code Without Reason

If existing code works and the task does not require architectural change:

Do not rewrite it simply because you prefer another style.

Prefer incremental improvements.

---

# 69. Documentation Updates

If implementation changes behavior documented in:

```text
PRODUCT.md
ARCHITECTURE.md
DATABASE.md
UI.md
SECURITY.md
API.md
```

update the affected document.

Documentation is part of the implementation.

---

# 70. API Changes

Before changing an API endpoint:

1. Check `docs/API.md`.
2. Determine whether the change is breaking.
3. Update API documentation.
4. Update backend implementation.
5. Update frontend client/types.
6. Update tests.

Do not silently change response shapes.

---

# 71. Database Changes

Before changing the database:

1. Check `DATABASE.md`.
2. Update model.
3. Generate migration.
4. Review migration.
5. Update affected services.
6. Update API schemas.
7. Update tests.
8. Update documentation.

---

# 72. Security Changes

If a change affects:

* authentication
* authorization
* face data
* location
* attendance verification
* rate limiting
* session management

review `SECURITY.md`.

Update it when the threat model or implementation materially changes.

---

# 73. UI Changes

If a new screen or reusable UI pattern is introduced:

1. Check `UI.md`.
2. Follow existing design conventions.
3. Update `UI.md` if the new pattern becomes part of the product design system.

---

# 74. Do Not Invent Requirements

If the product specification does not define something:

Do not automatically invent a large feature.

Examples:

Do not add:

* notifications
* chat
* messaging
* timetables
* parent accounts
* AI analytics
* payroll
* payment systems

unless explicitly requested.

---

# 75. MVP Discipline

Prioritize the core workflow:

```text
Authentication
      ↓
Academic setup
      ↓
Face registration
      ↓
Faculty session
      ↓
Student location verification
      ↓
Student face verification
      ↓
Attendance
      ↓
History
```

Do not build peripheral features before this workflow is stable.

---

# 76. No Fake Functionality

Never implement fake security.

Do not:

```python
face_verified = True
```

to bypass incomplete face recognition.

Do not:

```python
location_verified = True
```

to bypass geolocation.

Do not create fake successful API responses merely to make the UI work.

If a subsystem is not implemented, make the limitation explicit.

---

# 77. Development Stubs

Temporary development stubs are allowed only when clearly isolated.

Example:

```text
backend/app/dev/
```

or a clearly documented development-only dependency.

They must:

* Never run in production
* Be clearly named
* Be easy to remove
* Not weaken production security

---

# 78. Logging

Use structured logging where practical.

Useful:

```text
request_id
user_id
route
status
duration
error_code
```

Never log:

```text
face embedding
face image
OAuth token
session token
authorization header
database password
```

---

# 79. Error Handling

Expected business errors should become stable API error codes.

Example:

```text
SESSION_EXPIRED
```

not:

```text
ValueError("oops")
```

Unexpected errors should be logged internally and returned as safe generic errors.

---

# 80. Observability

The system should eventually expose enough information to diagnose:

* API failures
* Database errors
* Face processing latency
* Attendance failures
* Rate limiting
* Authentication issues

without collecting unnecessary sensitive data.

---

# 81. Dependency Management

Before adding a dependency:

Ask:

1. Is it actually necessary?
2. Is the functionality already available?
3. Is it maintained?
4. Does it introduce security concerns?
5. Does it increase deployment complexity?

Do not add dependencies for trivial functionality.

---

# 82. Frontend Dependency Rules

Avoid adding another state-management library.

Current intended stack:

```text
TanStack Query → Server state
Zustand → Client state
React → Component state
```

Do not introduce Redux or another global state system unless explicitly requested.

---

# 83. Backend Dependency Rules

Avoid adding:

* Celery
* Redis
* Kafka
* RabbitMQ
* another database

unless a real requirement justifies it.

The initial architecture should remain a modular monolith.

---

# 84. Modular Monolith

The backend should initially be a modular monolith.

Conceptually:

```text
FastAPI
│
├── Auth
├── Students
├── Faculty
├── Academic
├── Attendance
├── Verification
├── Face
└── Admin
```

These are modules inside one backend application.

Do not split them into microservices prematurely.

---

# 85. API Module Organization

Possible structure:

```text
backend/app/api/
├── auth.py
├── students.py
├── faculty.py
├── attendance.py
├── verification.py
└── admin.py
```

As modules grow, they may be split into directories.

---

# 86. Feature-Oriented Backend Organization

Where appropriate:

```text
backend/app/
├── modules/
│   ├── auth/
│   ├── students/
│   ├── faculty/
│   ├── attendance/
│   ├── verification/
│   └── admin/
```

The exact structure may be chosen during implementation.

The important rule is separation of responsibilities.

---

# 87. Code Review Before Completion

Before considering a task complete, check:

```text
[ ] Requirement implemented
[ ] Documentation still accurate
[ ] Security implications considered
[ ] API contract respected
[ ] Database changes migrated
[ ] Tests added/updated
[ ] Type errors resolved
[ ] Lint errors resolved
[ ] No secrets committed
[ ] No debug code
[ ] No unnecessary dependencies
```

---

# 88. Verification Before Claiming Completion

Do not say:

> "Implemented successfully"

unless the implementation has actually been verified.

Run appropriate:

```text
Frontend
- typecheck
- lint
- tests
- build

Backend
- type checking if configured
- lint
- tests
- migration checks
```

If something cannot be run, clearly state that.

---

# 89. Handling Failures

If a test/build/check fails:

1. Read the actual error.
2. Identify the root cause.
3. Fix the root cause.
4. Re-run the check.
5. Do not suppress the error merely to obtain a passing build.

Avoid:

```text
# noqa
# type: ignore
any
```

as shortcuts unless justified.

---

# 90. Minimal Change Principle

When fixing a bug:

Prefer:

```text
Smallest correct fix
```

over:

```text
Rewrite the subsystem
```

unless the current architecture makes the fix unsafe or impossible.

---

# 91. When Requirements Conflict

If two documents appear to conflict:

1. Identify the conflict.
2. Determine which requirement is more recent/intentional.
3. Update documentation.
4. Implement the consistent design.

Do not maintain contradictory behavior.

---

# 92. When Information Is Missing

If implementation requires an important product decision that cannot safely be inferred:

Ask for clarification.

Examples:

* Attendance policy
* Institutional grading rule
* Biometric retention period
* Faculty permissions
* Admin permissions
* Session overlap behavior
* Legal/privacy requirements

Do not silently make consequential policy decisions.

---

# 93. Safe Assumptions

For minor implementation details, reasonable assumptions are allowed.

Examples:

* Component naming
* File naming
* Internal helper structure
* Small UI spacing
* Internal function organization

Document meaningful assumptions when they affect architecture.

---

# 94. Never Expose Sensitive Data

Treat the following as sensitive:

```text
OAuth credentials
Session tokens
Face embeddings
Raw face images
Private student information
Private location data
Database credentials
Arcjet credentials
```

Do not expose them in:

* API responses
* Logs
* Git
* Screenshots
* Error messages
* Debug output

unless explicitly required and authorized.

---

# 95. Security-Critical Code Requires Extra Care

Security-sensitive changes include:

```text
Authentication
Authorization
Face verification
Location verification
Attendance creation
Session handling
Rate limiting
Biometric storage
```

For these changes:

* Read `SECURITY.md`.
* Add tests.
* Avoid shortcuts.
* Verify failure cases.
* Consider race conditions.
* Consider malicious clients.

---

# 96. Attendance Is Not Ordinary CRUD

Treat attendance as a protected business workflow.

The final operation:

```text
attendance created
```

must only happen after all required verification conditions have passed.

---

# 97. Definition of Done — Attendance

A student attendance feature is not complete until:

```text
[ ] Student is authenticated
[ ] Student is authorized
[ ] Session is active
[ ] Student is enrolled
[ ] Verification context is valid
[ ] Location is verified
[ ] Face is verified
[ ] Duplicate attendance is prevented
[ ] Attendance is stored transactionally
[ ] API returns correct status
[ ] Frontend reflects actual backend result
[ ] Failure states are handled
[ ] Tests cover security boundaries
```

---

# 98. Definition of Done — Feature

A general feature is complete when:

```text
[ ] Requirement implemented
[ ] Backend implemented
[ ] Frontend implemented where required
[ ] API contract updated
[ ] Database migration created if needed
[ ] Tests added
[ ] Loading states implemented
[ ] Error states implemented
[ ] Authorization verified
[ ] Responsive UI checked
[ ] Documentation updated
```

---

# 99. Codex Working Style

When working on GeoAttend:

Be:

```text
Precise
Incremental
Security-conscious
Documentation-driven
Test-driven where practical
```

Avoid:

```text
Overengineering
Premature abstraction
Silent architectural changes
Fake functionality
Large unrelated rewrites
```

---

# 100. Final Rule

Before writing code, understand the system.

Before changing architecture, explain the reason.

Before trusting data, verify its source.

Before marking attendance, verify the student.

Before claiming completion, run the checks.

And above all:

> **Do not make the system easier to code at the expense of making attendance easier to fake.**
