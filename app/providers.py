from typing import Iterable

from dishka import Provider, Scope, provide
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.task_service import TaskService

from app.interfaces.task_repository import ITaskRepository

from app.interfaces.user_repository import IUserRepository

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
    def get_task_repository(self, db: Session) -> ITaskRepository:
        return TaskRepository(db)

    @provide(scope=Scope.REQUEST)
    def get_user_repository(self, db: Session) -> IUserRepository:
        return UserRepository(db)

    @provide(scope=Scope.REQUEST)
    def get_task_service(self, repo: ITaskRepository) -> TaskService:
        return TaskService(repo)

    @provide(scope=Scope.REQUEST)
    def get_auth_service(self, repo: IUserRepository) -> AuthService:
        return AuthService(repo)
