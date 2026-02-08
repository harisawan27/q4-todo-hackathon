"""Task business logic orchestrator — coordinates state + events."""

import logging
from datetime import datetime, timezone
from typing import Optional

from app.models.events import TaskEventType
from app.models.task import Task, TaskCreate, TaskPriority, TaskStatus, TaskUpdate
from app.services import pubsub_service, state_service

logger = logging.getLogger("chat-api")


async def create_task(user_id: str, task_data: TaskCreate) -> Task:
    """Create a new task, save state, and publish events."""
    task = Task(
        user_id=user_id,
        title=task_data.title,
        description=task_data.description,
        priority=task_data.priority,
        due_date=task_data.due_date,
        due_time=task_data.due_time,
        tags=task_data.tags,
    )
    await state_service.save_task(task)

    event_data = {
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "priority": task.priority.value if task.priority else None,
        "dueDate": task.due_date.isoformat() if task.due_date else None,
        "tags": task.tags,
        "recurrenceRule": task_data.recurrence_rule,
        "etag": task.etag,
    }
    await pubsub_service.publish_task_event(TaskEventType.CREATED, task, event_data)
    await pubsub_service.publish_task_update_broadcast("created", task)

    logger.info(f"Task created: {task.id} - {task.title}")
    return task


async def get_task(task_id: str) -> Optional[Task]:
    """Get a task by ID."""
    result = await state_service.get_task(task_id)
    if result is None:
        return None
    task, etag = result
    task.etag = etag
    return task


async def list_tasks(user_id: str) -> list[Task]:
    """List all tasks for a user."""
    return await state_service.list_user_tasks(user_id)


async def update_task(task_id: str, user_id: str, updates: TaskUpdate, etag: str | None = None) -> Optional[Task]:
    """Update a task, publish events."""
    result = await state_service.get_task(task_id)
    if result is None:
        return None

    task, current_etag = result
    if task.user_id != user_id:
        return None

    before = {}
    after = {}
    changed_fields = []

    update_dict = updates.model_dump(exclude_none=True)
    for field, new_value in update_dict.items():
        old_value = getattr(task, field)
        if old_value != new_value:
            before[field] = str(old_value) if old_value is not None else None
            after[field] = str(new_value) if new_value is not None else None
            changed_fields.append(field)
            setattr(task, field, new_value)

    if not changed_fields:
        return task

    task.updated_at = datetime.now(timezone.utc)
    await state_service.update_task(task, etag or current_etag)

    event_data = {
        "before": before,
        "after": after,
        "changedFields": changed_fields,
        "etag": task.etag,
    }
    await pubsub_service.publish_task_event(TaskEventType.UPDATED, task, event_data)
    await pubsub_service.publish_task_update_broadcast("updated", task)

    logger.info(f"Task updated: {task.id} - fields: {changed_fields}")
    return task


async def complete_task(task_id: str, user_id: str, etag: str | None = None) -> Optional[Task]:
    """Mark a task as completed, publish events."""
    result = await state_service.get_task(task_id)
    if result is None:
        return None

    task, current_etag = result
    if task.user_id != user_id:
        return None

    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.now(timezone.utc)
    task.updated_at = datetime.now(timezone.utc)

    await state_service.update_task(task, etag or current_etag)

    has_recurrence = task.recurrence_rule_id is not None
    event_data = {
        "title": task.title,
        "completedAt": task.completed_at.isoformat(),
        "hasRecurrence": has_recurrence,
        "etag": task.etag,
    }
    await pubsub_service.publish_task_event(TaskEventType.COMPLETED, task, event_data)
    await pubsub_service.publish_task_update_broadcast("completed", task)

    logger.info(f"Task completed: {task.id} - {task.title}")
    return task


async def delete_task(task_id: str, user_id: str) -> bool:
    """Delete a task, publish events."""
    result = await state_service.get_task(task_id)
    if result is None:
        return False

    task, etag = result
    if task.user_id != user_id:
        return False

    await state_service.delete_task(task_id, user_id, etag)

    event_data = {
        "title": task.title,
        "deletedAt": datetime.now(timezone.utc).isoformat(),
    }
    await pubsub_service.publish_task_event(TaskEventType.DELETED, task, event_data)
    await pubsub_service.publish_task_update_broadcast("deleted", task)

    logger.info(f"Task deleted: {task.id} - {task.title}")
    return True


async def find_task_by_title(user_id: str, title: str) -> Optional[Task]:
    """Find a task by title (case-insensitive partial match)."""
    tasks = await list_tasks(user_id)
    title_lower = title.lower()
    for task in tasks:
        if task.title.lower() == title_lower or title_lower in task.title.lower():
            return task
    return None
