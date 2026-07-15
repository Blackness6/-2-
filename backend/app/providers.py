from typing import Iterable

from dishka import Provider, Scope, provide
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.repositories.project_repository import ProjectRepository
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.project_service import ProjectService
from app.services.task_service import TaskService

from app.interfaces.project_repository import IProjectRepository

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
    def get_task_service(
        self,
        db: Session,
        repo: ITaskRepository,
        user_repo: IUserRepository,
    ) -> TaskService:
        return TaskService(db, repo, user_repo)

    @provide(scope=Scope.REQUEST)
    def get_auth_service(self, db: Session, repo: IUserRepository) -> AuthService:
        return AuthService(db, repo)

    @provide(scope=Scope.REQUEST)
    def get_project_repository(self, db: Session) -> IProjectRepository:
        return ProjectRepository(db)

    @provide(scope=Scope.REQUEST)
    def get_project_service(
        self,
        db: Session,
        repo: IProjectRepository,
        user_repo: IUserRepository,
    ) -> ProjectService:
        return ProjectService(db, repo, user_repo)