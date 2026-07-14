from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Project, Task

from app.interfaces.project_repository import IProjectRepository

class ProjectRepository(IProjectRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.flush()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: int, user_id: int) -> Project | None:
        stmt = select(Project).where(
            Project.id == project_id,
            Project.owner_id == user_id,
        )
        return self.db.scalars(stmt).first()

    def get_all(self, user_id: int) -> list[Project]:
        stmt = (
            select(Project, func.count(Task.id))
            .outerjoin(Task, Task.project_id == Project.id)
            .where(Project.owner_id == user_id)
            .group_by(Project.id)
            .order_by(Project.created_at.desc())
        )
        projects = []
        for project, count in self.db.execute(stmt).all():
            project.task_count = count     # обычный атрибут — Pydantic его прочитает
            projects.append(project)
        return projects

    def update(self, project: Project) -> Project:
        self.db.flush()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.flush()
