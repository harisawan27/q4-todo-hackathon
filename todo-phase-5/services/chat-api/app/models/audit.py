"""Audit record models for task change tracking (P3 scope)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AuditAction(str, Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    COMPLETED = "COMPLETED"
    DELETED = "DELETED"
    RECURRENCE_GENERATED = "RECURRENCE_GENERATED"


class AuditRecord(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    event_id: str
    task_id: str
    user_id: str
    action: AuditAction
    timestamp: datetime
    change_summary: str
    before_state: Optional[dict] = None
    after_state: Optional[dict] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditIndex(BaseModel):
    """Index of audit record IDs for a task."""
    task_id: str
    record_ids: list[str] = Field(default_factory=list)
