"""FCM (Firebase Cloud Messaging) token model for push notifications"""

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import Field, SQLModel


class FCMToken(SQLModel, table=True):
    """
    Stores FCM device tokens for sending push notifications.
    Each user can have multiple tokens (multiple devices).
    """

    __tablename__ = "fcm_tokens"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    user_id: str = Field(index=True)
    token: str = Field(unique=True, index=True)  # FCM registration token
    platform: str = Field(default="android")  # android, ios, web
    device_info: Optional[str] = Field(default=None)  # Optional device identifier
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class FCMTokenCreate(SQLModel):
    """Schema for creating/registering an FCM token"""

    token: str
    platform: str = "android"
    device_info: Optional[str] = None


class FCMTokenResponse(SQLModel):
    """Schema for FCM token response"""

    id: str
    user_id: str
    token: str
    platform: str
    created_at: datetime
