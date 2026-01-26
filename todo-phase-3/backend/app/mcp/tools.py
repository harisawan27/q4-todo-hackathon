"""MCP tools for task management operations"""

import logging
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import Session, select

from ..database import engine
from ..models import Task

logger = logging.getLogger(__name__)


def list_tasks(user_id: str, status: str = "all") -> dict:
    """
    List tasks for a user with optional status filter.

    Args:
        user_id: The user's ID
        status: Filter by status - "all", "pending", or "completed"

    Returns:
        Dict with tasks list or error message
    """
    try:
        with Session(engine) as session:
            statement = select(Task).where(Task.user_id == user_id)

            if status == "pending":
                statement = statement.where(Task.completed == False)
            elif status == "completed":
                statement = statement.where(Task.completed == True)
            elif status != "all":
                return {"error": f"Invalid status '{status}'. Use 'all', 'pending', or 'completed'."}

            statement = statement.order_by(Task.created_at.desc())
            tasks = session.exec(statement).all()

            if not tasks:
                return {
                    "tasks": [],
                    "message": "You don't have any tasks yet. Would you like me to help you create one?"
                }

            task_list = []
            for task in tasks:
                task_info = {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "due_date": str(task.due_date) if task.due_date else None,
                    "tags": task.tags,
                }
                task_list.append(task_info)

            return {
                "tasks": task_list,
                "count": len(task_list),
                "status_filter": status
            }

    except Exception as e:
        logger.error(f"Error listing tasks: {e}")
        return {"error": f"Failed to retrieve tasks: {str(e)}"}


def add_task(user_id: str, title: str, description: Optional[str] = None) -> dict:
    """
    Add a new task for a user.

    Args:
        user_id: The user's ID
        title: Task title (required)
        description: Task description (optional)

    Returns:
        Dict with created task info or error message
    """
    if not title or not title.strip():
        return {"error": "Task title cannot be empty"}

    try:
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

            logger.info(f"Created task '{task.title}' for user {user_id}")

            return {
                "success": True,
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                },
                "message": f"Task '{task.title}' has been added."
            }

    except Exception as e:
        logger.error(f"Error adding task: {e}")
        return {"error": f"Failed to create task: {str(e)}"}


def complete_task(user_id: str, task_id: str) -> dict:
    """
    Mark a task as completed.

    Args:
        user_id: The user's ID
        task_id: The task's ID

    Returns:
        Dict with result or error message
    """
    try:
        with Session(engine) as session:
            task = session.get(Task, task_id)

            if not task:
                return {"error": "No matching task found."}

            if task.user_id != user_id:
                return {"error": "No matching task found."}

            if task.completed:
                return {
                    "success": True,
                    "message": f"Task '{task.title}' is already marked as complete."
                }

            task.completed = True
            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()

            logger.info(f"Completed task '{task.title}' for user {user_id}")

            return {
                "success": True,
                "message": f"Task '{task.title}' has been marked as complete."
            }

    except Exception as e:
        logger.error(f"Error completing task: {e}")
        return {"error": f"Failed to complete task: {str(e)}"}


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
        task_id: The task's ID
        title: New title (optional)
        description: New description (optional)

    Returns:
        Dict with result or error message
    """
    if not title and description is None:
        return {"error": "No fields provided to update. Specify title or description."}

    try:
        with Session(engine) as session:
            task = session.get(Task, task_id)

            if not task:
                return {"error": "No matching task found."}

            if task.user_id != user_id:
                return {"error": "No matching task found."}

            changes = []
            if title:
                task.title = title.strip()
                changes.append(f"title to '{task.title}'")

            if description is not None:
                task.description = description.strip() if description else None
                changes.append("description")

            task.updated_at = datetime.now(timezone.utc)
            session.add(task)
            session.commit()

            logger.info(f"Updated task '{task.title}' for user {user_id}: {', '.join(changes)}")

            return {
                "success": True,
                "message": f"Task updated: {', '.join(changes)}.",
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                }
            }

    except Exception as e:
        logger.error(f"Error updating task: {e}")
        return {"error": f"Failed to update task: {str(e)}"}


def delete_task(user_id: str, task_id: str) -> dict:
    """
    Delete a task.

    Args:
        user_id: The user's ID
        task_id: The task's ID

    Returns:
        Dict with result or error message
    """
    try:
        with Session(engine) as session:
            task = session.get(Task, task_id)

            if not task:
                return {"error": "No matching task found."}

            if task.user_id != user_id:
                return {"error": "No matching task found."}

            task_title = task.title
            session.delete(task)
            session.commit()

            logger.info(f"Deleted task '{task_title}' for user {user_id}")

            return {
                "success": True,
                "message": f"Task '{task_title}' has been deleted."
            }

    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        return {"error": f"Failed to delete task: {str(e)}"}


def find_task_by_title(user_id: str, title_query: str) -> dict:
    """
    Find a task by searching its title.

    Args:
        user_id: The user's ID
        title_query: Search query for task title

    Returns:
        Dict with matching task(s) or error message
    """
    try:
        with Session(engine) as session:
            statement = select(Task).where(
                Task.user_id == user_id,
                Task.title.ilike(f"%{title_query}%")
            )
            tasks = session.exec(statement).all()

            if not tasks:
                return {"error": f"No task found matching '{title_query}'."}

            if len(tasks) == 1:
                task = tasks[0]
                return {
                    "task": {
                        "id": task.id,
                        "title": task.title,
                        "description": task.description,
                        "completed": task.completed,
                    }
                }

            # Multiple matches - return list for clarification
            return {
                "multiple_matches": True,
                "tasks": [
                    {"id": t.id, "title": t.title, "completed": t.completed}
                    for t in tasks
                ],
                "message": f"Found {len(tasks)} tasks matching '{title_query}'. Please specify which one."
            }

    except Exception as e:
        logger.error(f"Error finding task: {e}")
        return {"error": f"Failed to find task: {str(e)}"}
