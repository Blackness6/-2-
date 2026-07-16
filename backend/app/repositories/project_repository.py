from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models import Project, ProjectMember, Task

from app.interfaces.project_repository import IProjectRepository


class ProjectRepository(IProjectRepository):
    def __init__(self, db: Session):
        self.db = db

    def _member_exists(self, user_id: int):
        """Коррелированный EXISTS: текущий пользователь — участник проекта."""
        return (
            select(ProjectMember.id)
            .where(
                ProjectMember.project_id == Project.id,
                ProjectMember.user_id == user_id,
            )
            .exists()
        )

    def create(self, project: Project) -> Project:
        self.db.add(project)
        self.db.flush()
        self.db.refresh(project)
        return project

    def get_by_id(self, project_id: int, user_id: int) -> Project | None:
        # Доступ: владелец ИЛИ участник
        stmt = select(Project).where(
            Project.id == project_id,
            or_(Project.owner_id == user_id, self._member_exists(user_id)),
        )
        return self.db.scalars(stmt).first()

    def get_all(self, user_id: int) -> list[Project]:
        stmt = (
            select(Project, func.count(Task.id))
            .outerjoin(Task, Task.project_id == Project.id)
            .where(or_(Project.owner_id == user_id, self._member_exists(user_id)))
            .group_by(Project.id)
            .order_by(Project.created_at.desc())
        )
        projects = []
        for project, count in self.db.execute(stmt).all():
            project.task_count = count
            projects.append(project)
        return projects

    def update(self, project: Project) -> Project:
        self.db.flush()
        self.db.refresh(project)
        return project

    def delete(self, project: Project) -> None:
        self.db.delete(project)
        self.db.flush()

    # ---------- участники ----------

    def get_member(self, project_id: int, user_id: int) -> ProjectMember | None:
        stmt = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        return self.db.scalars(stmt).first()

    def list_members(self, project_id: int) -> list[ProjectMember]:
        stmt = (
            select(ProjectMember)
            .where(ProjectMember.project_id == project_id)
            .options(selectinload(ProjectMember.user))
            .order_by(ProjectMember.created_at.asc())
        )
        return list(self.db.scalars(stmt).all())

    def add_member(self, member: ProjectMember) -> ProjectMember:
        self.db.add(member)
        self.db.flush()
        self.db.refresh(member)
        return member

    def remove_member(self, member: ProjectMember) -> None:
        self.db.delete(member)
        self.db.flush()