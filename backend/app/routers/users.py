from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter, Depends

from app.core.security import get_current_user_id
from app.interfaces.user_repository import IUserRepository
from app.schemas import UserShortResponse

router = APIRouter(
    prefix="/api/users",
    tags=["users"],
    route_class=DishkaRoute,
)


# Список пользователей — чтобы на frontend выбрать исполнителя задачи
@router.get("", response_model=list[UserShortResponse])
def get_users(
    repo: FromDishka[IUserRepository],
    user_id: int = Depends(get_current_user_id),
):
    return repo.get_all()
