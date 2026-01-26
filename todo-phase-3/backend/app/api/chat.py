"""Chat API endpoints"""

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ..agent.runner import run_agent

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., min_length=1, max_length=4000)
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response: str
    conversation_id: str


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(user_id: str, request: ChatRequest) -> ChatResponse:
    """
    Process a chat message and return the agent's response.

    Args:
        user_id: The authenticated user's ID
        request: Chat request with message and optional conversation_id

    Returns:
        ChatResponse with agent response and conversation_id
    """
    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty"
        )

    logger.info(f"Chat request from user {user_id}")

    try:
        result = run_agent(
            user_id=user_id,
            message=request.message.strip(),
            conversation_id=request.conversation_id,
        )

        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
        )

    except Exception as e:
        logger.error(f"Chat error for user {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process chat request"
        )
