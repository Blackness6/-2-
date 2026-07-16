from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import User

from app.interfaces.user_repository import IUserRepository


class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalars(
            select(User).where(User.email == email)
        ).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def get_all(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.username)).all())
