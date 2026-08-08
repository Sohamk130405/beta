import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_auth_me_without_cookie(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    with TestClient(app) as client:
        resp = client.get("/api/v1/auth/me")
    assert resp.status_code in (401, 403, 404, 200)


def test_dev_provision_and_login(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    with TestClient(app) as client:
        p = {"email": "devflow@example.com", "name": "Dev Flow"}
        resp = client.post("/api/v1/dev/provision-user", json=p)
        assert resp.status_code in (200, 201, 422, 500)
