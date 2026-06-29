from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.user_repository import UserRepository
from app.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
)
from app.services.auth_service import AuthSrevice

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)
@router.post("/register", response_model=UserResponse, status_code=201,) 

def register(
    data: UserCreate,
    db: Session = Depends(get_db),):

    repository = UserRepository(db)
    service = AuthService(repository)

    return service.register(data)

@router.post(
    "/login",
    response_modal=Token,)

def login(  
    data UserLogib,
    db: Sesssion = Depends(get_db),):
repository = UserRepository(db)
service = AuthService(repository)

token = service.login(data)

return {"access_token": token, "token_type": "bearer",}

