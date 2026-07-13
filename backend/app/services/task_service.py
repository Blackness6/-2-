from datetime import datetime, timezone

from fastapi import HTTPException
from fastapi import status as http_status  # переименовали чтобы не конфликтовало
from sqlalchemy.orm import Session

from app.models import Task

from app.schemas import TaskAssign, TaskCreate, TaskUpdate, TaskStats

from app.interfaces.task_repository import ITaskRepository
from app.interfaces.user_repository import IUserRepository

def _utcnow() -> datetime:
    """Текущее время UTC без tzinfo (совместимо с SQLite)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class TaskService:
    def __init__(self, db: Session, repo: ITaskRepository, user_repo: IUserRepository):
        self.db = db
        self.repo = repo
        self.user_repo = user_repo

    def _ensure_user_exists(self, user_id: int) -> None:
        if self.user_repo.get_by_id(user_id) is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"User {user_id} not found",
            )

    def create_task(self, data: TaskCreate, user_id: int) -> Task:
        now = _utcnow()

        # Исполнитель опционален: если выбран — проверяем, что такой пользователь есть,
        # и запоминаем, кто его назначил (текущий пользователь из JWT).
        assignee_id = None
        assigned_by_id = None
        if data.assignee_id is not None:
            self._ensure_user_exists(data.assignee_id)
            assignee_id = data.assignee_id
            assigned_by_id = user_id

        task = Task(
            title=data.title,
            description=data.description,
            status="TODO",
            priority=data.priority,
            created_at=now,
            updated_at=now,
            creator_id=user_id,
            assignee_id=assignee_id,
            assigned_by_id=assigned_by_id,
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

    def assign_task(self, task_id: int, data: TaskAssign, user_id: int) -> Task:
        task = self.get_task(task_id, user_id)

        # Назначать (и переназначать) исполнителя может только создатель задачи.
        if task.creator_id != user_id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Only the task creator can assign it",
            )

        self._ensure_user_exists(data.assignee_id)

        task.assignee_id = data.assignee_id
        task.assigned_by_id = user_id
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

        # Удалять задачу может только её создатель.
        if task.creator_id != user_id:
            raise HTTPException(
                status_code=http_status.HTTP_403_FORBIDDEN,
                detail="Only the task creator can delete it",
            )

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
