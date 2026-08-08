import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_admin_institution_create_requires_admin(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/admin/institutions", json={"name": "X", "code": "X"}
        )
    assert resp.status_code in (401, 403)
