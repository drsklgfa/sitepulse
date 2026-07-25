from __future__ import annotations

import os
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test_sitepulse.db"
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["SEED_DEMO_DATA"] = "false"
os.environ["CELERY_ALWAYS_EAGER"] = "true"
os.environ["ALLOW_PRIVATE_NETWORKS"] = "true"
os.environ["ALLOWED_PRIVATE_HOSTS"] = "localhost,demo-target"
os.environ["RETRY_BACKOFF_SECONDS"] = "0"

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def reset_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "tester@example.com", "password": "StrongPass123!", "display_name": "Tester"},
    )
    assert response.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "tester@example.com", "password": "StrongPass123!"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}
