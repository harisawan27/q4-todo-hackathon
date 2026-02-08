"""Dapr Jobs API payload models."""

from typing import Any, Optional

from pydantic import BaseModel


class JobRegistration(BaseModel):
    """Payload for registering a job via Dapr Jobs API."""
    schedule: Optional[str] = None
    repeats: Optional[int] = None
    due_time: Optional[str] = None
    ttl: Optional[str] = None
    data: dict[str, Any] = {}


class JobCallback(BaseModel):
    """Payload received when a Dapr Job fires."""
    data: dict[str, Any] = {}
