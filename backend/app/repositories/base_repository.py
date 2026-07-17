from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import Base

T = TypeVar("T", bound=Base)


class BaseModelRepository(Generic[T]):

    model: type[T]

    def __init__(self, db: Session):
        self.db = db

    def create(self, obj: T) -> T:
        self.db.add(obj)
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def get_by_id_raw(self, object_id: int) -> T | None:
        return self.db.get(self.model, object_id)

    def get_all_raw(self) -> list[T]:
        return list(self.db.scalars(select(self.model)).all())

    def update(self, obj: T) -> T:
        self.db.flush()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: T) -> None:
        self.db.delete(obj)
        self.db.flush()