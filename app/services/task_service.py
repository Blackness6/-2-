from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi import status as http_status  # переименовали чтобы не конфликтовало

from app.models import Task

from app.schemas import TaskCreate, TaskUpdate, TaskStats

from app.interfaces.task_repository import ITaskRepository

def _utcnow() -> datetime:
    """Текущее время UTC без tzinfo (совместимо с SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TaskService:
    def __init__(self, repo: ITaskRepository):
        self.repo = repo

    def create_task(self, data: TaskCreate) -> Task:
        now = _utcnow()
        task = Task(
            title=data.title,
            description=data.description,
            status="TODO",
            priority=data.priority,
            created_at=now,
            updated_at=now,
        )
        return self.repo.create(task)

    def get_tasks(
        self,
        status: str | None = None,
        priority: int | None = None,
    ) -> list[Task]:
        return self.repo.get_all(status=status, priority=priority)

    def get_task(self, task_id: int) -> Task:
        task = self.repo.get_by_id(task_id)
        if task is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        return task

    def update_task(self, task_id: int, data: TaskUpdate) -> Task:
        task = self.get_task(task_id)
        update_data = data.model_dump(exclude_none=True)
        for field, value in update_data.items():
            setattr(task, field, value)
        task.updated_at = _utcnow()
        return self.repo.update(task)

    def delete_task(self, task_id: int) -> None:
        task = self.get_task(task_id)
        self.repo.delete(task)

    def get_stats(self) -> TaskStats:
        raw = self.repo.get_stats()
        return TaskStats(
            TODO=raw.get("TODO", 0),
            IN_PROGRESS=raw.get("IN_PROGRESS", 0),
            DONE=raw.get("DONE", 0),
            CANCELLED=raw.get("CANCELLED", 0),
        )