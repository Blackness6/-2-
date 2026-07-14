from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from app.core.security import get_current_user_id
from app.schemas import (ProjectCreate, ProjectUpdate, ProjectResponse, TaskCreate, TaskResponse,)
from app.services.project_service import ProjectService

from app.services.task_service import TaskService

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
    route_class=DishkaRoute,
)


@router.post("", response_model=ProjectResponse, status_code=201)
def create_project(
    data: ProjectCreate,
    service: FromDishka[ProjectService],
    user_id: int = Depends(get_current_user_id),
):
    return service.create_project(data, user_id)


@router.get("", response_model=list[ProjectResponse])
def get_projects(
    service: FromDishka[ProjectService],
    user_id: int = Depends(get_current_user_id),
):
    return service.get_projects(user_id)


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    service: FromDishka[ProjectService],
    user_id: int = Depends(get_current_user_id),
):
    return service.get_project(project_id, user_id)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    service: FromDishka[ProjectService],
    user_id: int = Depends(get_current_user_id),
):
    return service.update_project(project_id, data, user_id)


@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    service: FromDishka[ProjectService],
    user_id: int = Depends(get_current_user_id),
):
    service.delete_project(project_id, user_id)

@router.post("/{project_id}/tasks", response_model=TaskResponse, status_code=201)
def create_project_task(
    project_id: int,
    data: TaskCreate,
    project_service: FromDishka[ProjectService],
    task_service: FromDishka[TaskService],
    user_id: int = Depends(get_current_user_id),
):
    project_service.get_project(project_id, user_id) # 404, если не владелец
    return task_service.create_task(data, user_id, project_id)

@router.get("/{project_id}/tasks", response_model=list[TaskResponse])
def get_project_tasks(
    project_id: int,
    project_service: FromDishka[ProjectService],
    task_service: FromDishka[TaskService],
    user_id: int = Depends(get_current_user_id),
):
    project_service.get_project(project_id, user_id)
    return task_service.get_tasks(user_id=user_id, project_id=project_id)