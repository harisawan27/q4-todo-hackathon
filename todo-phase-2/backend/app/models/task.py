"""Task model and schemas for the Todo application"""

from datetime import datetime, timezone, date, time
from typing import Optional, List
from uuid import uuid4
from enum import Enum

from pydantic import field_validator
from sqlmodel import Field, SQLModel, Column, JSON
from sqlalchemy import String


class Priority(str, Enum):
    """Task priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskCreate(SQLModel):
    """Request schema for creating a task - only title required"""

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = Field(default=None)
    due_time: Optional[time] = Field(default=None)
    priority: Optional[Priority] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)

    @field_validator("title", mode="before")
    @classmethod
    def validate_title_not_empty(cls, v: str) -> str:
        """Ensure title is not just whitespace"""
        if isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("Title cannot be empty or whitespace")
            return stripped
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace from description"""
        if v is not None and isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> List[str]:
        """Validate and clean tags"""
        if v is None:
            return []
        if isinstance(v, list):
            cleaned = []
            seen = set()
            for tag in v:
                if isinstance(tag, str):
                    tag = tag.strip().lower()
                    if tag and tag not in seen and len(tag) <= 50:
                        cleaned.append(tag)
                        seen.add(tag)
            return cleaned[:10]
        return []


class Task(SQLModel, table=True):
    """Database task model - only title is required"""

    __tablename__ = "tasks"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    title: str = Field(max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = Field(default=None)
    due_time: Optional[time] = Field(default=None)
    priority: Optional[str] = Field(default=None, sa_column=Column(String(10)))
    tags: List[str] = Field(default=[], sa_column=Column(JSON))
    completed: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class TaskUpdate(SQLModel):
    """Request schema for updating a task (partial)"""

    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = Field(default=None, max_length=2000)
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    completed: Optional[bool] = None

    @field_validator("title", mode="before")
    @classmethod
    def validate_title_not_empty(cls, v: Optional[str]) -> Optional[str]:
        """Ensure title is not just whitespace if provided"""
        if v is not None and isinstance(v, str):
            stripped = v.strip()
            if not stripped:
                raise ValueError("Title cannot be empty or whitespace")
            return stripped
        return v

    @field_validator("description", mode="before")
    @classmethod
    def validate_description(cls, v: Optional[str]) -> Optional[str]:
        """Strip whitespace from description"""
        if v is not None and isinstance(v, str):
            stripped = v.strip()
            return stripped if stripped else None
        return v

    @field_validator("tags", mode="before")
    @classmethod
    def validate_tags(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        """Validate and clean tags"""
        if v is None:
            return None
        if isinstance(v, list):
            cleaned = []
            seen = set()
            for tag in v:
                if isinstance(tag, str):
                    tag = tag.strip().lower()
                    if tag and tag not in seen and len(tag) <= 50:
                        cleaned.append(tag)
                        seen.add(tag)
            return cleaned[:10]
        return None


class TaskRead(SQLModel):
    """Response schema for reading a task"""

    id: str
    user_id: str
    title: str
    description: Optional[str] = None
    due_date: Optional[date] = None
    due_time: Optional[time] = None
    priority: Optional[str] = None
    tags: List[str] = []
    completed: bool
    created_at: datetime
    updated_at: datetime
