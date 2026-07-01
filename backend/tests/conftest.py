from typing import Iterable

import pytest
from dishka import Provider, Scope, make_async_container, provide
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.security import get_current_user_id
from app.database import Base
from app.main import app
from app.providers import AppProvider

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = sessionmaker(bind=engine)


class TestDatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_session(self) -> Iterable[Session]:
        db = TestSessionLocal()
        try:
            yield db
        finally:
            db.close()


@pytest.fixture
def client():
    Base.metadata.create_all(bind=engine)

    container = make_async_container(TestDatabaseProvider(), AppProvider())
    app.state.dishka_container = container  # middleware already added in main.py

    app.dependency_overrides[get_current_user_id] = lambda: 1

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
