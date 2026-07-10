from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi import status as http_status  # переименовали чтобы не конфликтовало
from sqlalchemy.orm import Session

from app.models import Task

from app.schemas import TaskCreate, TaskUpdate, TaskStats

from app.interfaces.task_repository import ITaskRepository

def _utcnow() -> datetime:
    """Текущее время UTC без tzinfo (совместимо с SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TaskService:
    def __init__(self, db: Session, repo: ITaskRepository):
        self.db = db
        self.repo = repo

    def create_task(self, data: TaskCreate, user_id: int) -> Task:
        now = _utcnow()
        task = Task(
            title=data.title,
            description=data.description,
            status="TODO",
            priority=data.priority,
            created_at=now,
            updated_at=now,
            user_id=user_id,
        )
        try:
            task = self.repo.create(task)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return task

    def get_tasks(
        self,
        user_id: int,
        status: str | None = None,
        priority: int | None = None,
    ) -> list[Task]:
        return self.repo.get_all(user_id=user_id, status=status, priority=priority)

    def get_task(self, task_id: int, user_id: int) -> Task:
        task = self.repo.get_by_id(task_id, user_id)
        if task is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        return task

    def update_task(self, task_id: int, data: TaskUpdate, user_id: int) -> Task:
        task = self.get_task(task_id, user_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        task.updated_at = _utcnow()
        try:
            task = self.repo.update(task)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return task

    def delete_task(self, task_id: int, user_id: int) -> None:
        task = self.get_task(task_id, user_id)
        try:
            self.repo.delete(task)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise

    def get_stats(self, user_id: int) -> TaskStats:
        raw = self.repo.get_stats(user_id)
        return TaskStats(
            TODO=raw.get("TODO", 0),
            IN_PROGRESS=raw.get("IN_PROGRESS", 0),
            DONE=raw.get("DONE", 0),
            CANCELLED=raw.get("CANCELLED", 0),
        )