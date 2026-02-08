"""Dapr Pub/Sub wrapper for publishing task events and broadcasts."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from app import dapr_client
from app.models.events import TaskEvent, TaskEventType, TaskUpdateBroadcast
from app.models.task import Task

logger = logging.getLogger("chat-api")


async def _safe_publish(topic: str, data: dict, metadata: dict | None = None) -> bool:
    """Publish to Dapr pub/sub with graceful failure handling (FR-009).

    Task operations should succeed even if the event bus is unavailable.
    Returns True if publish succeeded, False otherwise.
    """
    try:
        await dapr_client.publish_event(topic=topic, data=data, metadata=metadata)
        return True
    except Exception as e:
        logger.error(f"Failed to publish to topic '{topic}': {e}. Event will be lost.")
        return False


async def publish_task_event(event_type: TaskEventType, task: Task, extra_data: dict[str, Any] | None = None) -> None:
    """Publish a task lifecycle event to the task-events topic."""
    event = TaskEvent(
        event_type=event_type,
        task_id=task.id,
        user_id=task.user_id,
        data=extra_data or {},
    )
    cloud_event = {
        "specversion": "1.0",
        "id": event.event_id,
        "source": "chat-api",
        "type": f"com.donekaro.{event_type.value}",
        "datacontenttype": "application/json",
        "time": event.timestamp.isoformat(),
        "data": event.model_dump(mode="json"),
    }
    await _safe_publish(
        topic="task-events",
        data=cloud_event,
        metadata={"partitionKey": task.id},
    )


async def publish_task_update_broadcast(action: str, task: Task) -> None:
    """Publish a task update broadcast for real-time client updates."""
    broadcast = TaskUpdateBroadcast(
        user_id=task.user_id,
        data={
            "action": action,
            "taskId": task.id,
            "task": {
                "id": task.id,
                "title": task.title,
                "status": task.status.value,
                "priority": task.priority.value if task.priority else None,
                "dueDate": task.due_date.isoformat() if task.due_date else None,
                "tags": task.tags,
            } if action != "deleted" else None,
        },
    )
    cloud_event = {
        "specversion": "1.0",
        "id": broadcast.event_id,
        "source": "chat-api",
        "type": "com.donekaro.task-update.broadcast",
        "datacontenttype": "application/json",
        "time": broadcast.timestamp.isoformat(),
        "data": broadcast.model_dump(mode="json"),
    }
    await _safe_publish(topic="task-updates", data=cloud_event)


async def publish_raw_event(topic: str, cloud_event: dict[str, Any]) -> None:
    """Publish a raw CloudEvents envelope to a topic."""
    await _safe_publish(topic=topic, data=cloud_event)
