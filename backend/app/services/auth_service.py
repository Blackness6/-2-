from fastapi import HTTPException
from fastapi import status as http_status
from sqlalchemy.orm import Session

from app.core.security import (hash_password, verify_password , create_access_token,)
from app.models import User

from app.schemas import UserCreate, UserLogin

from app.interfaces.user_repository import IUserRepository


class AuthService:
    def __init__(self, db: Session, repository: IUserRepository):
        self.db = db
        self.repository= repository

    def register(self, data: UserCreate) -> User:

        existing_user = self.repository.get_by_email(data.email)

        if existing_user:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        user = User(
           username=data.username,
           email=data.email,
           hashed_password=hash_password(data.password),
        )
        try:
            user = self.repository.create(user)
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return user

    def login(self, data: UserLogin) -> str:
        user = self.repository.get_by_email(data.email)
        
        if user is None:
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        
        if not verify_password(
            data.password,
            user.hashed_password,
        ):
            
            raise HTTPException(
                status_code=http_status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",)
        
        token =create_access_token({"sub": str(user.id)})
        return token
    
    def get_account(self, user_id: int) -> User:
        user = self.repository.get_by_id(user_id)

        if user is None:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return user