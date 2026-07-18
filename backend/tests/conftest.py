import os
import sys
import uuid
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app import models  # noqa: E402
from app.utils import hash_password, pwd_context  # noqa: E402


@pytest.fixture(autouse=True, scope="session")
def _fast_password_hashing():

    pwd_context.update(bcrypt__rounds=4)
    yield


@pytest.fixture(autouse=True, scope="session")
def _no_real_email():
    import unittest.mock as mock

    with mock.patch("app.utils._send_email", return_value=None):
        yield


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """A fresh SQLite database, created and torn down for each test."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """A TestClient whose get_db dependency is overridden to use db_session."""

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def register_user():
    """Factory fixture: register a user via the API and return the response JSON."""

    def _register(client: TestClient, **overrides):
        payload = {
            "username": f"user{uuid.uuid4().hex[:8]}",
            "display_name": "Test User",
            "email": f"{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPass123",
            "role": "READER",
        }
        payload.update(overrides)
        response = client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201, response.text
        return {**response.json(), "_password": payload["password"], "_email": payload["email"]}

    return _register


@pytest.fixture()
def auth_headers():
    """Factory fixture: log in and return an Authorization header dict."""

    def _login(client: TestClient, email: str, password: str) -> dict:
        response = client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _login


@pytest.fixture()
def make_admin(db_session: Session):
    """Factory fixture: insert an ADMIN user directly (registration blocks self-signup as admin)."""

    def _make(email: str = "admin@example.com", password: str = "AdminPass123"):
        admin = models.User(
            username=f"admin{uuid.uuid4().hex[:6]}",
            display_name="Admin",
            email=email,
            password=hash_password(password),
            role=models.UserRole.ADMIN,
            is_verified=True,
            is_active=True,
        )
        db_session.add(admin)
        db_session.commit()
        return admin

    return _make
