from typing import Iterable

from dishka import Provider, Scope, provide
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.task_service import TaskService


class DatabaseProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_session(self) -> Iterable[Session]:
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()


class AppProvider(Provider):
    @provide(scope=Scope.REQUEST)
    def get_task_repository(self, db: Session) -> TaskRepository:
        return TaskRepository(db)

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, db: Session) -> UserRepository:
        return UserRepository(db)

    @provide(scope=Scope.REQUEST)
    def get_task_service(self, repo: TaskRepository) -> TaskService:
        return TaskService(repo)

    @provide(scope=Scope.REQUEST)
    def get_auth_service(self, repo: UserRepository) -> AuthService:
        return AuthService(repo)
