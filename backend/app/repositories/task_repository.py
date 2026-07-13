from sqlalchemy import or_, select, func
from sqlalchemy.orm import Session, selectinload

from app.models import Task

from app.interfaces.task_repository import ITaskRepository


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


class TaskRepository(ITaskRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task

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
    ) -> list[Task]:
        stmt = _with_users(select(Task).where(_visible_to(user_id)))
        if status is not None:
            stmt = stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        return list(self.db.scalars(stmt).all())

    def update(self, task: Task) -> Task:
        self.db.flush()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.flush()

    def get_stats(self, user_id: int) -> dict[str, int]:
        """GROUP BY статус — SQL-агрегация (только видимые пользователю задачи)."""
        rows = self.db.execute(
            select(Task.status, func.count(Task.id).label("cnt"))
            .where(_visible_to(user_id))
            .group_by(Task.status)
        ).all()
        return {row.status: row.cnt for row in rows}
