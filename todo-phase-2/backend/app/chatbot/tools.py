"""MCP-style tools for AI chatbot task management"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import Session, select

from app.database import engine
from app.models.task import Task

logger = logging.getLogger(__name__)


def list_tasks(user_id: str, status: str = "all") -> dict:
    """
    List tasks for a user with optional status filter.

    Args:
        user_id: The user's ID
        status: Filter - "all", "pending", or "completed"

    Returns:
        Dict with tasks list and metadata
    """
    if status not in ["all", "pending", "completed"]:
        return {"error": f"Invalid status: {status}. Use 'all', 'pending', or 'completed'"}

    with Session(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)

        if status == "pending":
            statement = statement.where(Task.completed == False)
        elif status == "completed":
            statement = statement.where(Task.completed == True)

        statement = statement.order_by(Task.created_at.desc())
        tasks = session.exec(statement).all()

        if not tasks:
            return {
                "tasks": [],
                "count": 0,
                "status_filter": status,
                "message": "No tasks found. Would you like to create one?"
            }

        return {
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "completed": t.completed,
                    "due_date": str(t.due_date) if t.due_date else None,
                    "priority": t.priority,
                }
                for t in tasks
            ],
            "count": len(tasks),
            "status_filter": status,
        }


def add_task(user_id: str, title: str, description: Optional[str] = None) -> dict:
    """
    Create a new task for a user.

    Args:
        user_id: The user's ID
        title: Task title
        description: Optional task description

    Returns:
        Dict with created task info
    """
    if not title or not title.strip():
        return {"error": "Task title cannot be empty"}

    with Session(engine) as session:
        task = Task(
            id=str(uuid4()),
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            completed=False,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Created task '{title}' for user {user_id}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
            },
            "message": f"Task '{title}' created successfully!"
        }


def complete_task(user_id: str, task_id: str) -> dict:
    """
    Mark a task as completed.

    Args:
        user_id: The user's ID
        task_id: The task ID to complete

    Returns:
        Dict with result
    """
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return {"error": "No matching task found. Please check the task ID."}

        task.completed = True
        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()

        logger.info(f"Completed task '{task.title}' for user {user_id}")

        return {
            "success": True,
            "message": f"Task '{task.title}' marked as complete!"
        }


def update_task(
    user_id: str,
    task_id: str,
    title: Optional[str] = None,
    description: Optional[str] = None
) -> dict:
    """
    Update a task's title or description.

    Args:
        user_id: The user's ID
        task_id: The task ID to update
        title: New title (optional)
        description: New description (optional)

    Returns:
        Dict with updated task info
    """
    if title is None and description is None:
        return {"error": "No fields provided to update"}

    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return {"error": "No matching task found. Please check the task ID."}

        if title is not None:
            task.title = title.strip()
        if description is not None:
            task.description = description.strip() if description else None

        task.updated_at = datetime.now(timezone.utc)
        session.add(task)
        session.commit()
        session.refresh(task)

        logger.info(f"Updated task '{task.title}' for user {user_id}")

        return {
            "success": True,
            "task": {
                "id": task.id,
                "title": task.title,
                "description": task.description,
            },
            "message": f"Task updated successfully!"
        }


def delete_task(user_id: str, task_id: str) -> dict:
    """
    Delete a task.

    Args:
        user_id: The user's ID
        task_id: The task ID to delete

    Returns:
        Dict with result
    """
    with Session(engine) as session:
        task = session.exec(
            select(Task).where(Task.id == task_id, Task.user_id == user_id)
        ).first()

        if not task:
            return {"error": "No matching task found. Please check the task ID."}

        title = task.title
        session.delete(task)
        session.commit()

        logger.info(f"Deleted task '{title}' for user {user_id}")

        return {
            "success": True,
            "message": f"Task '{title}' deleted successfully!"
        }


def find_task_by_title(user_id: str, title_query: str) -> dict:
    """
    Search for tasks by title (fuzzy match).

    Args:
        user_id: The user's ID
        title_query: Search query for task title

    Returns:
        Dict with matching tasks
    """
    if not title_query or not title_query.strip():
        return {"error": "Search query cannot be empty"}

    query = title_query.strip().lower()

    with Session(engine) as session:
        tasks = session.exec(
            select(Task).where(Task.user_id == user_id)
        ).all()

        matches = [
            {
                "id": t.id,
                "title": t.title,
                "completed": t.completed,
            }
            for t in tasks
            if query in t.title.lower()
        ]

        if not matches:
            return {
                "matches": [],
                "message": f"No tasks found matching '{title_query}'"
            }

        return {
            "matches": matches,
            "count": len(matches),
        }
