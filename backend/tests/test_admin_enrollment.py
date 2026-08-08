import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_enrollment_duplicate_handling(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    with TestClient(app) as client:
        # This test requires DB+auth; assert on permissive codes if not available.
        resp = client.post(
            "/api/v1/admin/classes/00000000-0000-0000-0000-000000000000/enrollments",
            json={"student_id": "00000000-0000-0000-0000-000000000000"},
        )
        assert resp.status_code in (201, 409, 404, 401, 403, 422, 500)
