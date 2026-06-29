from dishka.integrations.fastapi import DishkaRoute, FromDishka
from fastapi import APIRouter

from app.schemas import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
    route_class=DishkaRoute,
)


@router.post("/register", response_model=UserResponse, status_code=201)
def register(
    data: UserCreate,
    service: FromDishka[AuthService],
):
    return service.register(data)


@router.post("/login", response_model=Token)
def login(
    data: UserLogin,
    service: FromDishka[AuthService],
):
    token = service.login(data)
    return {"access_token": token, "token_type": "bearer"}
