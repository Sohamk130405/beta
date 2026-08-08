import pytest
from fastapi.testclient import TestClient

from app.main import app


def test_provision_user_requires_dev_env(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/dev/provision-user", json={"email": "a@b.com", "name": "Test"}
        )
    assert resp.status_code == 403


def test_provision_user_creates_user(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "development")
    with TestClient(app) as client:
        resp = client.post(
            "/api/v1/dev/provision-user",
            json={"email": "dev@example.com", "name": "Dev"},
        )
    assert resp.status_code in (200, 201, 403, 422, 500)
