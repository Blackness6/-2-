from datetime import datetime

from sqlalchemy import BigInteger, Integer, String, Text, DateTime
from sqlalchemy.orm import mapped_column, Mapped

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    # BigInteger для PostgreSQL; SQLite требует INTEGER (не BIGINT) для autoincrement
    id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), "postgresql"),
        primary_key=True,
        autoincrement=True,
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="TODO")
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

