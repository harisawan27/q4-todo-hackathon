"""Push subscription models for Web Push API."""

import uuid
from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field


class PushSubscription(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    endpoint: str
    auth: str
    p256dh: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PushSubscriptionIndex(BaseModel):
    """Index of push subscription IDs for a user."""
    user_id: str
    subscription_ids: list[str] = Field(default_factory=list)
