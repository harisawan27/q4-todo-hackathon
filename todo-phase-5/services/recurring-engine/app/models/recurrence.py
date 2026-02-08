"""Recurrence rule models for recurring task scheduling."""

import uuid
from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class RecurrenceFrequency(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    WEEKDAY = "weekday"
    MONTHLY = "monthly"
    CUSTOM = "custom"


class RecurrenceEndCondition(str, Enum):
    NEVER = "never"
    COUNT = "count"
    DATE = "date"


class RecurrenceRule(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str
    user_id: str
    frequency: RecurrenceFrequency
    interval: int = 1
    days_of_week: Optional[list[int]] = None
    day_of_month: Optional[int] = None
    time_of_day: str = "09:00"
    timezone: str = "UTC"
    cron_expression: Optional[str] = None
    end_condition: RecurrenceEndCondition = RecurrenceEndCondition.NEVER
    end_count: Optional[int] = None
    end_date: Optional[date] = None
    instances_generated: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    job_name: Optional[str] = None


class RecurrenceRuleCreate(BaseModel):
    frequency: RecurrenceFrequency
    interval: int = 1
    days_of_week: Optional[list[int]] = None
    day_of_month: Optional[int] = None
    time_of_day: str = "09:00"
    timezone: str = "UTC"
    cron_expression: Optional[str] = None
    end_condition: RecurrenceEndCondition = RecurrenceEndCondition.NEVER
    end_count: Optional[int] = None
    end_date: Optional[date] = None
