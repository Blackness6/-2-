from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.models import Project

from app.schemas import ProjectCreate, ProjectUpdate

from app.interfaces.project_repository import IProjectRepository


def _utcnow() -> datetime:
    """Текущее время UTC без tzinfo (совместимо с SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class ProjectService:
    def __init__(self, db: Session, repo: IProjectRepository):
        self.db = db
        self.repo = repo

    def create_project(self, data: ProjectCreate, user_id: int) -> Project:
        now = _utcnow()

        project = Project(
            name=data.name,
            description=data.description,
            owner_id=user_id,
            created_at=now,
            updated_at=now,
        )
        try:
            project = self.repo.create(project)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return project

    def get_projects(self, user_id: int) -> list[Project]:
        return self.repo.get_all(user_id)

    def get_project(self, project_id: int, user_id: int) -> Project:
        project = self.repo.get_by_id(project_id, user_id)
        if project is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found",
            )
        return project

    def update_project(self, project_id: int, data: ProjectUpdate, user_id: int) -> Project:
        project = self.get_project(project_id, user_id)
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        project.updated_at = _utcnow()
        try:
            project = self.repo.update(project)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return project

    def delete_project(self, project_id: int, user_id: int) -> None:
        project = self.get_project(project_id, user_id)

        try:
            self.repo.delete(project)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
