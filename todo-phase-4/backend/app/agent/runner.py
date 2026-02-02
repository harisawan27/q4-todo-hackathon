"""Agent runner using LiteLLM for natural language task management

Supports multiple LLM providers via LiteLLM:
- Google Gemini (default): gemini/gemini-1.5-flash
- OpenAI: gpt-4o-mini, gpt-4o
- Anthropic: claude-3-sonnet, claude-3-opus
"""

import json
import logging
import os
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

import litellm
from sqlmodel import Session, select

from ..config import settings
from ..database import engine
from ..models import Conversation, Message, MessageRole
from ..mcp.tools import (
    list_tasks,
    add_task,
    complete_task,
    update_task,
    delete_task,
    find_task_by_title,
)

# Configure LiteLLM
# Set API keys from settings
if settings.gemini_api_key:
    os.environ["GEMINI_API_KEY"] = settings.gemini_api_key
if settings.openai_api_key:
    os.environ["OPENAI_API_KEY"] = settings.openai_api_key

# Disable LiteLLM telemetry
litellm.telemetry = False

logger = logging.getLogger(__name__)

# System prompt for the agent
SYSTEM_PROMPT = """You are a helpful todo assistant. You help users manage their tasks through natural language conversation.

You have access to the following tools:
- list_tasks: Show the user's tasks (can filter by status: all, pending, completed)
- add_task: Create a new task with a title and optional description
- complete_task: Mark a task as done
- update_task: Change a task's title or description
- delete_task: Remove a task
- find_task_by_title: Search for a task by title

When users ask to see their tasks, use list_tasks.
When users want to add/create/remind about something, use add_task.
When users say "done", "complete", "finished", use complete_task.
When users want to change/edit/update a task, use update_task.
When users want to delete/remove a task, use delete_task.

Always confirm actions with the user. Be friendly and helpful.
If a task title is ambiguous, use find_task_by_title first to identify the correct task.

Format task lists in a readable way:
- Show task title, status (✓ or ○), and description if present
- Group by status if showing all tasks"""

# Tool definitions for OpenAI
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List the user's tasks with optional status filter",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["all", "pending", "completed"],
                        "description": "Filter tasks by status"
                    }
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "Optional task description"
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID to complete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update a task's title or description",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID to update"
                    },
                    "title": {
                        "type": "string",
                        "description": "New task title"
                    },
                    "description": {
                        "type": "string",
                        "description": "New task description"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "string",
                        "description": "The task ID to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "find_task_by_title",
            "description": "Search for a task by its title",
            "parameters": {
                "type": "object",
                "properties": {
                    "title_query": {
                        "type": "string",
                        "description": "Search query for task title"
                    }
                },
                "required": ["title_query"]
            }
        }
    }
]


def get_conversation_history(conversation_id: str, limit: int = 20) -> list[dict]:
    """
    Retrieve conversation history from database.

    Args:
        conversation_id: The conversation ID
        limit: Maximum number of messages to retrieve

    Returns:
        List of message dicts for OpenAI format
    """
    with Session(engine) as session:
        statement = (
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
        )
        messages = session.exec(statement).all()

        # Reverse to get chronological order
        messages = list(reversed(messages))

        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]


def save_message(
    conversation_id: str,
    user_id: str,
    role: MessageRole,
    content: str
) -> Message:
    """
    Save a message to the database.

    Args:
        conversation_id: The conversation ID
        user_id: The user ID
        role: Message role (user/assistant)
        content: Message content

    Returns:
        The saved Message object
    """
    with Session(engine) as session:
        message = Message(
            id=str(uuid4()),
            conversation_id=conversation_id,
            user_id=user_id,
            role=role,
            content=content,
            created_at=datetime.now(timezone.utc),
        )
        session.add(message)

        # Update conversation timestamp
        conversation = session.get(Conversation, conversation_id)
        if conversation:
            conversation.updated_at = datetime.now(timezone.utc)
            session.add(conversation)

        session.commit()
        session.refresh(message)
        return message


def get_or_create_conversation(
    user_id: str,
    conversation_id: Optional[str] = None
) -> Conversation:
    """
    Get existing conversation or create a new one.

    Args:
        user_id: The user ID
        conversation_id: Optional existing conversation ID

    Returns:
        Conversation object
    """
    with Session(engine) as session:
        if conversation_id:
            conversation = session.get(Conversation, conversation_id)
            if conversation and conversation.user_id == user_id:
                return conversation

        # Create new conversation
        conversation = Conversation(
            id=str(uuid4()),
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(conversation)
        session.commit()
        session.refresh(conversation)

        logger.info(f"Created new conversation {conversation.id} for user {user_id}")
        return conversation


def execute_tool(user_id: str, tool_name: str, arguments: dict) -> str:
    """
    Execute a tool function and return the result as JSON string.

    Args:
        user_id: The user ID for scoping operations
        tool_name: Name of the tool to execute
        arguments: Tool arguments

    Returns:
        JSON string of the tool result
    """
    try:
        if tool_name == "list_tasks":
            result = list_tasks(user_id, arguments.get("status", "all"))
        elif tool_name == "add_task":
            result = add_task(
                user_id,
                arguments["title"],
                arguments.get("description")
            )
        elif tool_name == "complete_task":
            result = complete_task(user_id, arguments["task_id"])
        elif tool_name == "update_task":
            result = update_task(
                user_id,
                arguments["task_id"],
                arguments.get("title"),
                arguments.get("description")
            )
        elif tool_name == "delete_task":
            result = delete_task(user_id, arguments["task_id"])
        elif tool_name == "find_task_by_title":
            result = find_task_by_title(user_id, arguments["title_query"])
        else:
            result = {"error": f"Unknown tool: {tool_name}"}

        return json.dumps(result)
    except Exception as e:
        logger.error(f"Tool execution error: {e}")
        return json.dumps({"error": str(e)})


def run_agent(user_id: str, message: str, conversation_id: Optional[str] = None) -> dict:
    """
    Run the agent to process a user message.

    5-step request cycle:
    1. Fetch conversation history
    2. Append user message
    3. Run LLM agent with tools (via LiteLLM)
    4. Store response & tool outputs
    5. Return response

    Args:
        user_id: The user ID
        message: The user's message
        conversation_id: Optional existing conversation ID

    Returns:
        Dict with response and conversation_id
    """
    # Step 1: Get or create conversation and fetch history
    conversation = get_or_create_conversation(user_id, conversation_id)
    history = get_conversation_history(conversation.id)

    # Step 2: Append user message to database
    save_message(conversation.id, user_id, MessageRole.USER, message)

    # Build messages for LLM
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history)
    messages.append({"role": "user", "content": message})

    logger.info(f"Processing message for user {user_id} with model {settings.llm_model}: {message[:50]}...")

    # Step 3: Run LLM agent via LiteLLM
    try:
        response = litellm.completion(
            model=settings.llm_model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
        )

        assistant_message = response.choices[0].message

        # Handle tool calls
        while assistant_message.tool_calls:
            # Add assistant message with tool calls
            messages.append({
                "role": "assistant",
                "content": assistant_message.content,
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Execute each tool call
            for tool_call in assistant_message.tool_calls:
                tool_name = tool_call.function.name
                arguments = json.loads(tool_call.function.arguments)

                logger.info(f"Executing tool: {tool_name} with args: {arguments}")

                tool_result = execute_tool(user_id, tool_name, arguments)

                # Add tool result to messages
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_result,
                })

            # Get next response
            response = litellm.completion(
                model=settings.llm_model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
            )
            assistant_message = response.choices[0].message

        # Final response content
        response_content = assistant_message.content or "I processed your request."

    except Exception as e:
        logger.error(f"Agent error: {e}")
        response_content = "I'm sorry, I encountered an error processing your request. Please try again."

    # Step 4: Store assistant response
    save_message(conversation.id, user_id, MessageRole.ASSISTANT, response_content)

    logger.info(f"Agent response for user {user_id}: {response_content[:50]}...")

    # Step 5: Return response
    return {
        "response": response_content,
        "conversation_id": conversation.id,
    }
