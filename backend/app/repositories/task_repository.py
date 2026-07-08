from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models import Task

from app.interfaces.task_repository import ITaskRepository 


class TaskRepository(ITaskRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, task: Task) -> Task:
        self.db.add(task)
        self.db.flush()
        self.db.refresh(task)
        return task

    def get_by_id(self, task_id: int) -> Task | None:
        return self.db.get(Task, task_id)


    def update(self, task: Task) -> Task:
        self.db.flush()
        self.db.refresh(task)
        return task

    def delete(self, task: Task) -> None:
        self.db.delete(task)
        self.db.flush()

    def get_stats(self) -> dict[str, int]:
        """GROUP BY статус — SQL-агрегация."""
        rows = self.db.execute(
            select(Task.status, func.count(Task.id).label("cnt"))
            .group_by(Task.status)
        ).all()
        return {row.status: row.cnt for row in rows}
    