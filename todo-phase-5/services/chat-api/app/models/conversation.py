"""Conversation context models for chatbot session management."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"


class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConversationContext(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    messages: list[Message] = Field(default_factory=list)
    current_intent: Optional[str] = None
    extracted_entities: dict = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def add_message(self, role: MessageRole, content: str) -> None:
        """Add a message, trimming oldest if over 50 messages."""
        self.messages.append(Message(role=role, content=content))
        if len(self.messages) > 50:
            self.messages = self.messages[-50:]
        self.updated_at = datetime.now(timezone.utc)
