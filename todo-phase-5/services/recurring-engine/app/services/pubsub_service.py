"""Dapr Pub/Sub wrapper for recurring-engine event publishing."""

import uuid
from datetime import datetime, timezone
from typing import Any

from app import dapr_client


async def publish_task_event(event_type: str, data: dict[str, Any], task_id: str = "") -> None:
    """Publish a task event to the task-events topic."""
    cloud_event = {
        "specversion": "1.0",
        "id": str(uuid.uuid4()),
        "source": "recurring-engine",
        "type": f"com.donekaro.{event_type}",
        "datacontenttype": "application/json",
        "time": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    metadata = {"partitionKey": task_id} if task_id else None
    await dapr_client.publish_event(topic="task-events", data=cloud_event, metadata=metadata)


async def publish_reminder_event(event_type: str, data: dict[str, Any]) -> None:
    """Publish a reminder event to the reminders topic."""
    cloud_event = {
        "specversion": "1.0",
        "id": str(uuid.uuid4()),
        "source": "recurring-engine",
        "type": f"com.donekaro.reminder.{event_type}",
        "datacontenttype": "application/json",
        "time": datetime.now(timezone.utc).isoformat(),
        "data": data,
    }
    await dapr_client.publish_event(topic="reminders", data=cloud_event)
