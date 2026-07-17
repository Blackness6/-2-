from sqlalchemy import or_, select, func
from sqlalchemy.orm import selectinload

from app.models import Task

from app.interfaces.task_repository import ITaskRepository
from app.repositories.base_repository import BaseModelRepository


def _visible_to(user_id: int):
    """Пользователь видит задачу, если он её создатель или исполнитель."""
    return or_(Task.creator_id == user_id, Task.assignee_id == user_id)

def _with_users(stmt):
    """Жадно подгружаем creator/assigned_by/assignee для сериализации ответа."""
    return stmt.options(
        selectinload(Task.creator),
        selectinload(Task.assigned_by),
        selectinload(Task.assignee),
    )

class TaskRepository(BaseModelRepository[Task], ITaskRepository):
    model = Task

    def get_by_id(self, task_id: int, user_id: int) -> Task | None:
        stmt = _with_users(
            select(Task).where(Task.id == task_id, _visible_to(user_id))
        )
        return self.db.scalars(stmt).first()

    def get_all(
        self,
        user_id: int,
        status: str | None = None,
        priority: int | None = None,
        project_id: int | None = None,
    ) -> list[Task]:
        stmt = _with_users(select(Task).where(_visible_to(user_id)))
        if status is not None:
            stmt = stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        if project_id is not None:
            stmt = stmt.where(Task.project_id == project_id)
        return list(self.db.scalars(stmt).all())

    def get_stats(self, user_id: int) -> dict[str, int]:
        """GROUP BY статус — SQL-агрегация (только видимые пользователю задачи)."""
        rows = self.db.execute(
            select(Task.status, func.count(Task.id).label("cnt"))
            .where(_visible_to(user_id))
            .group_by(Task.status)
        ).all()
        return {row.status: row.cnt for row in rows}

    def get_by_project(self, project_id: int) -> list[Task]:
        """Все задачи проекта (для его участников)."""
        stmt = _with_users(select(Task).where(Task.project_id == project_id))
        return list(self.db.scalars(stmt).all())