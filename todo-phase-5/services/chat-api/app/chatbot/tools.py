"""LiteLLM tool functions for chatbot task operations."""

import json
import logging
from datetime import date
from typing import Optional

from app.models.task import TaskCreate, TaskPriority, TaskUpdate
from app.services import task_service

logger = logging.getLogger("chat-api")

# Global user_id set by the runner before tool execution
_current_user_id: str = ""


def set_current_user(user_id: str) -> None:
    global _current_user_id
    _current_user_id = user_id


async def add_task(
    title: str,
    description: str = "",
    priority: str = "medium",
    due_date: str = "",
    tags: str = "",
) -> str:
    """Create a new task for the user.

    Args:
        title: The task title (required)
        description: Optional task description
        priority: Priority level: low, medium, high, urgent
        due_date: Optional due date in YYYY-MM-DD format
        tags: Comma-separated tags
    """
    try:
        task_data = TaskCreate(
            title=title,
            description=description if description else None,
            priority=TaskPriority(priority) if priority else None,
            due_date=date.fromisoformat(due_date) if due_date else None,
            tags=[t.strip() for t in tags.split(",") if t.strip()] if tags else [],
        )
        task = await task_service.create_task(_current_user_id, task_data)
        return json.dumps({"status": "created", "task_id": task.id, "title": task.title})
    except Exception as e:
        logger.error(f"Failed to create task: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def list_tasks() -> str:
    """List all tasks for the current user."""
    try:
        tasks = await task_service.list_tasks(_current_user_id)
        task_list = [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value,
                "priority": t.priority.value if t.priority else None,
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "tags": t.tags,
            }
            for t in tasks
        ]
        return json.dumps({"status": "success", "tasks": task_list, "count": len(task_list)})
    except Exception as e:
        logger.error(f"Failed to list tasks: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def complete_task(title: str) -> str:
    """Mark a task as completed by title.

    Args:
        title: The title of the task to complete
    """
    try:
        task = await task_service.find_task_by_title(_current_user_id, title)
        if task is None:
            return json.dumps({"status": "not_found", "message": f"No task found matching '{title}'"})

        completed = await task_service.complete_task(task.id, _current_user_id)
        if completed:
            has_recurrence = completed.recurrence_rule_id is not None
            return json.dumps({
                "status": "completed",
                "task_id": completed.id,
                "title": completed.title,
                "hasRecurrence": has_recurrence,
            })
        return json.dumps({"status": "error", "message": "Failed to complete task"})
    except Exception as e:
        logger.error(f"Failed to complete task: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def update_task(
    title: str,
    new_title: str = "",
    new_description: str = "",
    new_priority: str = "",
) -> str:
    """Update an existing task by title.

    Args:
        title: The current title of the task to update
        new_title: New title (optional)
        new_description: New description (optional)
        new_priority: New priority: low, medium, high, urgent (optional)
    """
    try:
        task = await task_service.find_task_by_title(_current_user_id, title)
        if task is None:
            return json.dumps({"status": "not_found", "message": f"No task found matching '{title}'"})

        updates = TaskUpdate(
            title=new_title if new_title else None,
            description=new_description if new_description else None,
            priority=TaskPriority(new_priority) if new_priority else None,
        )
        updated = await task_service.update_task(task.id, _current_user_id, updates)
        if updated:
            return json.dumps({"status": "updated", "task_id": updated.id, "title": updated.title})
        return json.dumps({"status": "error", "message": "Failed to update task"})
    except Exception as e:
        logger.error(f"Failed to update task: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def delete_task(title: str) -> str:
    """Delete a task by title.

    Args:
        title: The title of the task to delete
    """
    try:
        task = await task_service.find_task_by_title(_current_user_id, title)
        if task is None:
            return json.dumps({"status": "not_found", "message": f"No task found matching '{title}'"})

        deleted = await task_service.delete_task(task.id, _current_user_id)
        if deleted:
            return json.dumps({"status": "deleted", "title": task.title})
        return json.dumps({"status": "error", "message": "Failed to delete task"})
    except Exception as e:
        logger.error(f"Failed to delete task: {e}")
        return json.dumps({"status": "error", "message": str(e)})


async def find_task_by_title(title: str) -> str:
    """Find a task by its title.

    Args:
        title: The title to search for
    """
    try:
        task = await task_service.find_task_by_title(_current_user_id, title)
        if task is None:
            return json.dumps({"status": "not_found", "message": f"No task found matching '{title}'"})
        return json.dumps({
            "status": "found",
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status.value,
                "priority": task.priority.value if task.priority else None,
                "due_date": task.due_date.isoformat() if task.due_date else None,
                "tags": task.tags,
            },
        })
    except Exception as e:
        logger.error(f"Failed to find task: {e}")
        return json.dumps({"status": "error", "message": str(e)})


# Tool definitions for LiteLLM
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Create a new task for the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The task title"},
                    "description": {"type": "string", "description": "Optional task description"},
                    "priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "Priority level"},
                    "due_date": {"type": "string", "description": "Due date in YYYY-MM-DD format"},
                    "tags": {"type": "string", "description": "Comma-separated tags"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks for the current user",
            "parameters": {"type": "object", "properties": {}},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed by its title",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the task to complete"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task's title, description, or priority",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "Current title of the task to update"},
                    "new_title": {"type": "string", "description": "New title"},
                    "new_description": {"type": "string", "description": "New description"},
                    "new_priority": {"type": "string", "enum": ["low", "medium", "high", "urgent"], "description": "New priority"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by its title",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title of the task to delete"},
                },
                "required": ["title"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "find_task_by_title",
            "description": "Find a task by its title",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "The title to search for"},
                },
                "required": ["title"],
            },
        },
    },
]

# Map of function names to async callables
TOOL_MAP = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "update_task": update_task,
    "delete_task": delete_task,
    "find_task_by_title": find_task_by_title,
}
