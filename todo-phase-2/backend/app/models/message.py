"""Message model for AI chatbot conversations"""

from datetime import datetime, timezone
from enum import Enum
from uuid import uuid4

from sqlmodel import Field, SQLModel


class MessageRole(str, Enum):
    """Message role in conversation"""
    USER = "user"
    ASSISTANT = "assistant"


class Message(SQLModel, table=True):
    """Database model for chat messages"""

    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    conversation_id: str = Field(index=True)
    user_id: str = Field(index=True)
    role: MessageRole
    content: str
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
