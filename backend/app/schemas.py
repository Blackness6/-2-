from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# =========================
# ENUM
# =========================

class TaskStatus(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class TaskPriorityEnum(int, Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3


# =========================
# USER SCHEMAS
# =========================

class UserCreate(BaseModel):
    username: str = Field(
        ...,
        min_length=3,
        max_length=100,
    )

    email: EmailStr

    password: str = Field(
        ...,
        min_length=8,
    )


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str

    model_config = ConfigDict(
        from_attributes=True,
    )


# Короткая информация о пользователе внутри задачи
class UserShortResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config = ConfigDict(
        from_attributes=True,
    )


# =========================
# TASK SCHEMAS
# =========================

class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM

    # Кому назначается задача
    assignee_id: int | None = Field(
        default=None,
        gt=0,
    )


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None

    status: TaskStatus | None = None

    priority: TaskPriorityEnum | None = None


# Отдельная схема для назначения, переназначения или снятия исполнителя.
# assignee_id = null означает "убрать исполнителя".
class TaskAssign(BaseModel):
    assignee_id: int | None = Field(
        default=None,
        gt=0,
    )


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriorityEnum

    # ID пользователей
    creator_id: int
    assigned_by_id: int | None
    assignee_id: int | None

    # Проект, к которому относится задача
    project_id: int | None

    # Полная информация для отображения на frontend
    creator: UserShortResponse
    assigned_by: UserShortResponse | None
    assignee: UserShortResponse | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class TaskStats(BaseModel):
    TODO: int = 0
    IN_PROGRESS: int = 0
    DONE: int = 0
    CANCELLED: int = 0


# =========================
# AUTH SCHEMAS
# =========================

class Token(BaseModel):
    access_token: str
    token_type: str


# =========================
# PROJECT SCHEMAS
# =========================

class ProjectCreate(BaseModel):
    name: str = Field(
        ...,
        min_length=1,
        max_length=255,
    )

    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=255,
    )

    description: str | None = None


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: str | None
    owner_id: int

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )

