from sqlalchemy import select

from app.models import User

from app.interfaces.user_repository import IUserRepository
from app.repositories.base_repository import BaseModelRepository


class UserRepository(BaseModelRepository[User], IUserRepository):
    model = User

    def get_by_id(self, user_id: int) -> User | None:
        return self.get_by_id_raw(user_id)

    def get_by_email(self, email: str) -> User | None:
        return self.db.scalars(
            select(User).where(User.email == email)
        ).first()

    def get_all(self) -> list[User]:
        return list(self.db.scalars(select(User).order_by(User.username)).all())