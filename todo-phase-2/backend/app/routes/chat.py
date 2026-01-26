"""Chat API endpoints for AI chatbot"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.chatbot.runner import run_agent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    """Request schema for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response schema for chat endpoint"""
    response: str
    conversation_id: Optional[str]


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(user_id: str, request: ChatRequest) -> ChatResponse:
    """
    Send a message to the AI chatbot.

    The chatbot can help manage tasks through natural language:
    - "Show me my tasks"
    - "Add a task: Buy groceries"
    - "Mark 'Buy groceries' as done"
    - "Delete the task 'Buy groceries'"
    """
    logger.info(f"Chat request from user {user_id}")

    # Validate message
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    # Run the agent
    result = run_agent(
        user_id=user_id,
        message=request.message.strip(),
        conversation_id=request.conversation_id,
    )

    return ChatResponse(
        response=result["response"],
        conversation_id=result["conversation_id"],
    )
