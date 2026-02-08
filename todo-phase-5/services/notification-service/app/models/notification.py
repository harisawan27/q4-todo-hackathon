"""Notification models for push notification delivery."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class NotificationType(str, Enum):
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_DELETED = "task_deleted"
    DEADLINE_APPROACHING = "deadline_approaching"
    DEADLINE_PASSED = "deadline_passed"
    RECURRENCE_GENERATED = "recurrence_generated"
    SYSTEM = "system"


class Notification(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    type: NotificationType
    task_id: Optional[str] = None
    reminder_level: Optional[str] = None
    read: bool = False
    delivered: bool = False
    delivered_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
