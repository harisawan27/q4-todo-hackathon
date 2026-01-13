"""Notification model and schemas for the Todo application"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4
from enum import Enum

from sqlmodel import Field, SQLModel


class NotificationType(str, Enum):
    """Types of notifications"""
    TASK_CREATED = "task_created"
    TASK_COMPLETED = "task_completed"
    TASK_DELETED = "task_deleted"
    DEADLINE_APPROACHING = "deadline_approaching"
    DEADLINE_PASSED = "deadline_passed"
    SYSTEM = "system"


class ReminderLevel(str, Enum):
    """
    Duolingo-style reminder levels before deadline.
    Each level triggers a notification/email at specific hours before deadline.
    """
    DAY_BEFORE = "day_before"        # 24 hours before
    HOURS_10 = "hours_10"            # 10 hours before
    HOURS_6 = "hours_6"              # 6 hours before
    HOURS_3 = "hours_3"              # 3 hours before
    HOURS_1 = "hours_1"              # 1 hour before
    OVERDUE = "overdue"              # Past deadline


# Reminder schedule: (level, hours_before_deadline)
REMINDER_SCHEDULE = [
    (ReminderLevel.DAY_BEFORE, 24),
    (ReminderLevel.HOURS_10, 10),
    (ReminderLevel.HOURS_6, 6),
    (ReminderLevel.HOURS_3, 3),
    (ReminderLevel.HOURS_1, 1),
    (ReminderLevel.OVERDUE, 0),
]


class NotificationCreate(SQLModel):
    """Schema for creating a notification internally"""
    user_id: str
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    type: NotificationType
    task_id: Optional[str] = None


class Notification(SQLModel, table=True):
    """Database notification model"""

    __tablename__ = "notifications"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=200)
    message: str = Field(max_length=1000)
    type: str = Field(max_length=30)
    task_id: Optional[str] = Field(default=None, index=True)
    reminder_level: Optional[str] = Field(default=None, max_length=20)  # Tracks which reminder level was sent
    read: bool = Field(default=False)
    email_sent: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class NotificationRead(SQLModel):
    """Response schema for reading a notification"""
    id: str
    user_id: str
    title: str
    message: str
    type: str
    task_id: Optional[str] = None
    read: bool
    created_at: datetime


class NotificationUpdate(SQLModel):
    """Schema for updating notification (mark as read)"""
    read: Optional[bool] = None
