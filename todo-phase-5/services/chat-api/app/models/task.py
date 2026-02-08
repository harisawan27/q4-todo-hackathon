"""Task domain models for Dapr State Management."""

import uuid
from datetime import date, datetime, time, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: TaskStatus = TaskStatus.PENDING
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    tags: list[str] = Field(default_factory=list)
    recurrence_rule_id: Optional[str] = None
    parent_task_id: Optional[str] = None
    instance_number: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    etag: Optional[str] = None


class TaskCreate(BaseModel):
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    tags: list[str] = Field(default_factory=list)
    recurrence_rule: Optional[dict] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    priority: Optional[TaskPriority] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    tags: Optional[list[str]] = None
    status: Optional[TaskStatus] = None


class TaskIndex(BaseModel):
    """Index of task IDs for a user. Stored at task-index--{user-id}."""
    user_id: str
    task_ids: list[str] = Field(default_factory=list)
