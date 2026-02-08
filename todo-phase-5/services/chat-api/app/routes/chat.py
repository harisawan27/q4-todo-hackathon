"""Chat endpoint for conversational task management."""

from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.chatbot.runner import process_message
from app.middleware.auth import get_current_user

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    message: str = Field(max_length=2000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    conversation_id: Optional[str] = None
    task_action: Optional[dict] = None


@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    request: ChatRequest,
    user_id: str = Depends(get_current_user),
):
    """Send a message to the AI chatbot for task management."""
    result = await process_message(
        user_id=user_id,
        message=request.message,
        conversation_id=request.conversation_id,
    )
    return ChatResponse(**result)
