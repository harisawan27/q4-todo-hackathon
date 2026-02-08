"""Event payload models for Dapr Pub/Sub CloudEvents."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class TaskEventType(str, Enum):
    CREATED = "task-created"
    UPDATED = "task-updated"
    COMPLETED = "task-completed"
    DELETED = "task-deleted"
    RECURRENCE_GENERATED = "task-recurrence-generated"


class TaskEvent(BaseModel):
    """CloudEvents data payload for task-events topic."""
    model_config = ConfigDict(extra="ignore")

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: TaskEventType
    task_id: str
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = Field(default_factory=dict)


class TaskUpdateBroadcast(BaseModel):
    """Payload for task-updates topic (real-time cross-client updates)."""
    model_config = ConfigDict(extra="ignore")

    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = "task-update-broadcast"
    user_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    data: dict[str, Any] = Field(default_factory=dict)
