from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

from pydantic import EmailStr 

TaskStatus = Literal["TODO", "IN_PROGRESS", "DONE", "CANCELLED"]
TaskPriority = Literal[1, 2, 3]


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    priority: TaskPriority = 2


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str | None
    status: TaskStatus    # было str
    priority: TaskPriority  # было int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskStats(BaseModel):
    TODO: int = 0
    IN_PROGRESS: int = 0
    DONE: int = 0
    CANCELLED: int = 0

