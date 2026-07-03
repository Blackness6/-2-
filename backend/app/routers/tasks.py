from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends, Query

from app.core.security import get_current_user_id
from app.schemas import TaskCreate, TaskUpdate, TaskResponse, TaskStats, TaskStatus
from app.services.task_service import TaskService

router = APIRouter(
    prefix="/api/tasks",
    tags=["tasks"],
    route_class=DishkaRoute,
    dependencies=[Depends(get_current_user_id)],
)


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    data: TaskCreate,
    service: FromDishka[TaskService],
):
    return service.create_task(data)




@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: int,
    service: FromDishka[TaskService],
):
    return service.get_task(task_id)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    data: TaskUpdate,
    service: FromDishka[TaskService],
):
    return service.update_task(task_id, data)


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: int,
    service: FromDishka[TaskService],
):
    service.delete_task(task_id)
