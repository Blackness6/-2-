from fastapi import HTTPException, status 

from app.core.security import (hash_password, verify_password , create_access_token,)
from app.models import User

from app.schemas import UserCreate, UserLogin

from app.interfaces.user_repository import IUserRepository


class AuthService:
    def __init__(self, repository: IUserRepository):
        self.repository= repository

    def register(self, data: UserCreate) -> User:

        existing_user = self.repository.get_by_email(data.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )  
        
        user = User(
           username=data.username,
           email=data.email,
           hashed_password=hash_password(data.password),
        )
        user = self.repository.create(user)
        self.repository.commit()
        return user

    def login(self, data: UserLogin) -> str:
        user = self.repository.get_by_email(data.email)
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        if not verify_password(
            data.password,
            user.hashed_password,
        ):
            
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",)
        
        token =create_access_token({"sub": str(user.id)})
        return token