from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), "postgresql"),
        primary_key=True,
        autoincrement=True,
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    role: Mapped[str] = mapped_column(
        String(20),
        default="user",
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    created_tasks: Mapped[List["Task"]] = relationship(
        back_populates="creator",
        foreign_keys="Task.creator_id",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    assigned_by_me_tasks: Mapped[List["Task"]] = relationship(
        back_populates="assigned_by",
        foreign_keys="Task.assigned_by_id",
    )

    assigned_to_me_tasks: Mapped[List["Task"]] = relationship(
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        Integer().with_variant(BigInteger(), "postgresql"),
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="TODO",
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=2,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    # Кто создал задачу
    creator_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    # Кто назначил текущего исполнителя
    assigned_by_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # Кто выполняет задачу
    assignee_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    # Объект пользователя-создателя
    creator: Mapped["User"] = relationship(
        back_populates="created_tasks",
        foreign_keys=[creator_id],
    )

    # Объект пользователя, который назначил
    assigned_by: Mapped[Optional["User"]] = relationship(
        back_populates="assigned_by_me_tasks",
        foreign_keys=[assigned_by_id],
    )

    # Объект пользователя-исполнителя
    assignee: Mapped[Optional["User"]] = relationship(
        back_populates="assigned_to_me_tasks",
        foreign_keys=[assignee_id],
    )