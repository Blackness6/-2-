from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.models import Project, ProjectMember

from app.schemas import ProjectCreate, ProjectUpdate, ProjectMemberCreate, ProjectRole

from app.interfaces.project_repository import IProjectRepository
from app.interfaces.user_repository import IUserRepository


def _utcnow() -> datetime:
    """Текущее время UTC без tzinfo (совместимо с SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


# Роли, которым разрешено создавать и назначать задачи в проекте.
_TASK_MANAGERS = {"owner", "manager"}


class ProjectService:
    def __init__(self, db: Session, repo: IProjectRepository, user_repo: IUserRepository):
        self.db = db
        self.repo = repo
        self.user_repo = user_repo

    # ---------- вспомогательные ----------

    def _role_of(self, project: Project, user_id: int) -> str | None:
        if project.owner_id == user_id:
            return "owner"
        member = self.repo.get_member(project.id, user_id)
        return member.role if member else None

    def _require_owner(self, project: Project, user_id: int) -> None:
        if project.owner_id != user_id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Only the project owner can perform this action",
            )

    # ---------- проекты ----------

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
        # Доступ: владелец ИЛИ участник (реализовано в repo.get_by_id)
        project = self.repo.get_by_id(project_id, user_id)
        if project is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found",
            )
        return project

    def update_project(self, project_id: int, data: ProjectUpdate, user_id: int) -> Project:
        project = self.get_project(project_id, user_id)   # 404, если нет доступа
        self._require_owner(project, user_id)             # изменять может только владелец
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
        self._require_owner(project, user_id)             # удалять может только владелец
        try:
            self.repo.delete(project)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    # ---------- участники ----------

    def list_members(self, project_id: int, user_id: int) -> list:
        project = self.get_project(project_id, user_id)   # доступ: владелец/участник
        # Владелец — синтетическая запись с ролью owner (в таблице не хранится)
        owner_entry = SimpleNamespace(
            id=None,
            project_id=project.id,
            user_id=project.owner_id,
            role="owner",
            user=project.owner,
        )
        members = self.repo.list_members(project_id)
        return [owner_entry, *members]

    def add_member(self, project_id: int, data: ProjectMemberCreate, user_id: int) -> ProjectMember:
        project = self.get_project(project_id, user_id)
        self._require_owner(project, user_id)             # добавлять может только владелец

        if data.role == ProjectRole.OWNER:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Cannot assign the 'owner' role",
            )

        if self.user_repo.get_by_id(data.user_id) is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"User {data.user_id} not found",
            )

        if data.user_id == project.owner_id:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Owner is already in the project",
            )

        if self.repo.get_member(project_id, data.user_id) is not None:
            raise HTTPException(
                status_code=http_status.HTTP_409_CONFLICT,
                detail="User is already a member of the project",
            )

        member = ProjectMember(
            project_id=project_id,
            user_id=data.user_id,
            role=data.role.value,
            created_at=_utcnow(),
        )
        try:
            member = self.repo.add_member(member)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return member

    def remove_member(self, project_id: int, member_user_id: int, user_id: int) -> None:
        project = self.get_project(project_id, user_id)
        self._require_owner(project, user_id)             # удалять может только владелец

        member = self.repo.get_member(project_id, member_user_id)
        if member is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="Member not found",
            )
        try:
            self.repo.remove_member(member)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def ensure_can_manage_tasks(self, project_id: int, user_id: int) -> Project:
        """Создавать/назначать задачи могут владелец и менеджер."""
        project = self.get_project(project_id, user_id)   # 404, если нет доступа
        if self._role_of(project, user_id) not in _TASK_MANAGERS:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="You are not allowed to create tasks in this project",
            )
        return project