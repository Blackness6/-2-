from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user_id
from app.schemas import TaskAssign, TaskCreate, TaskUpdate, TaskResponse, TaskStats, TaskStatus
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"],
    route_class=DishkaRoute,
)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    data: TaskCreate,
    service: FromDishka[TaskService],
    user_id: int = Depends(get_current_user_id),
):
    return service.create_task(data, user_id)


@router.get("/stats", response_model=TaskStats)
def get_stats(
    service: FromDishka[TaskService],
    user_id: int = Depends(get_current_user_id),
):
    return service.get_stats(user_id)


@router.get("", response_model=list[TaskResponse])
def get_tasks(
    service: FromDishka[TaskService],
    status: TaskStatus | None = Query(default=None),
    priority: int | None = Query(default=None),
    user_id: int = Depends(get_current_user_id),
):
    return service.get_tasks(user_id=user_id, status=status, priority=priority)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    service: FromDishka[TaskService],
    user_id: int = Depends(get_current_user_id),
):
    return service.get_task(task_id, user_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    service: FromDishka[TaskService],
    user_id: int = Depends(get_current_user_id),
):
    return service.update_task(task_id, data, user_id)


@router.patch("/{task_id}/assign", response_model=TaskResponse)
def assign_task(
    task_id: int,
    data: TaskAssign,
    service: FromDishka[TaskService],
    user_id: int = Depends(get_current_user_id),
):
    return service.assign_task(task_id, data, user_id)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    service: FromDishka[TaskService],
    user_id: int = Depends(get_current_user_id),
):
    service.delete_task(task_id, user_id)
