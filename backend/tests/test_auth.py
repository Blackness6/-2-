from typing import Iterable

import pytest
from dishka import Provider, Scope, make_async_container, provide
from fastapi.testclient import  TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.main import app
from app.providers import AppProvider

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(bind=engine)

class AuthDatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_session(self) -> Iterable[Session]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    container = make_async_container(AuthDatabaseProvider(), AppProvider())
    app.state.dishka_container = container

    app.dependency_overrides.clear()

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)

VALID_USER = {
    "username": "carol",
    "email": "carol@test.com",
    "password": "pasword123",
}


def register(client, **overrides):
    return client.post("/auth/register", json={**VALID_USER, **overrides})


def login(client, email=VALID_USER["email"], password=VALID_USER["password"]):
    return client.post("/auth/login", json={"email": email, "password": password})


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

# ─── register ─────────────────────────────────────────────────────────────────

def test_register_creates_user(client):
    resp = register(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "carol"
    assert data["email"] == "carol@test.com"
    assert data["role"] == "user"
    assert "id" in data
    # пароль/хеш не должны утекать в ответ
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email(client):
    register(client)
    resp = register(client, username="carol2")
    assert resp.status_code == 400
    assert resp.json()["detail"] == "Email already registered"


def test_register_short_password(client):
    resp = register(client, password="short")
    assert resp.status_code == 422


def test_register_invalid_email(client):
    resp = register(client, email="not-an-email")
    assert resp.status_code == 422


# ─── login ─────────────────────────────────────────────────────────────────

def test_login_returns_token(client):
    register(client)
    resp = login(client)
    assert resp.status_code == 200
    data = resp.json()
    assert data["token_type"] == "bearer"
    assert data["access_token"]


def test_login_wrong_password(client):
    register(client)
    resp = login(client, password="wrong-password")
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = login(client, email="ghost@test.com")
    assert resp.status_code == 401


# ─── /auth/me и защита эндпоинтов ────────────────────────────────────────────

def test_me_returns_current_user(client):
    register(client)
    token = login(client).json()["access_token"]
    resp = client.get("/auth/me", headers=auth_header(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "carol@test.com"
    assert data["username"] == "carol"


def test_protected_endpoint_requires_token(client):
    resp = client.get("/api/tasks")
    assert resp.status_code == 401


def test_protected_endpoint_rejects_invalid_token(client):
    resp = client.get("/api/tasks", headers=auth_header("garbage.token.value"))
    assert resp.status_code == 401


def test_valid_token_grants_access(client):
    register(client)
    token = login(client).json()["access_token"]
    resp = client.get("/api/tasks", headers=auth_header(token))
    assert resp.status_code == 200