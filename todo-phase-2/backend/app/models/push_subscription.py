"""Push subscription model for Web Push notifications"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import Field, SQLModel


class PushSubscription(SQLModel, table=True):
    """
    Store Web Push API subscriptions for browser notifications.
    Each user can have multiple subscriptions (different browsers/devices).
    """

    __tablename__ = "push_subscriptions"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)

    # Web Push subscription info
    endpoint: str = Field(max_length=500)  # Push service endpoint URL
    p256dh: str = Field(max_length=100)    # Public key for encryption
    auth: str = Field(max_length=50)       # Auth secret

    # Metadata
    user_agent: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


class PushSubscriptionCreate(SQLModel):
    """Schema for creating a push subscription"""
    endpoint: str
    keys: dict  # Contains p256dh and auth


class PushSubscriptionRead(SQLModel):
    """Response schema for reading a push subscription"""
    id: str
    user_id: str
    endpoint: str
    created_at: datetime
