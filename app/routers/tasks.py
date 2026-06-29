from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_user_id
from app.database import get_db
from app.repositories.task_repository import TaskRepository
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskStats, TaskStatus
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"],
    dependencies=[Depends(get_current_user_id)],
)


def get_service(db: Session = Depends(get_db)) -> TaskService:
    return TaskService(TaskRepository(db))


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    data: TaskCreate,
    service: Annotated[TaskService, Depends(get_service)],
):
    return service.create_task(data)


@router.get("/stats", response_model=TaskStats)
def get_stats(
    service: Annotated[TaskService, Depends(get_service)],
):
    """Статистика задач по статусам (GROUP BY)."""
    return service.get_stats()


@router.get("", response_model=list[TaskResponse])
def get_tasks(
    service: Annotated[TaskService, Depends(get_service)],
    status: TaskStatus | None = Query(default=None),  # было str | None
    priority: int | None = Query(default=None),
):
    return service.get_tasks(status=status, priority=priority)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    service: Annotated[TaskService, Depends(get_service)],
):
    return service.get_task(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    service: Annotated[TaskService, Depends(get_service)],
):
    return service.update_task(task_id, data)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    service: Annotated[TaskService, Depends(get_service)],
):
    service.delete_task(task_id)