"""Dapr event handler for task-updates topic — cross-client propagation."""

import logging

from fastapi import APIRouter, Request

from app.services import push_service

logger = logging.getLogger("notification-service")

router = APIRouter(tags=["Events"])


@router.post("/events/task-updates")
async def handle_task_updates(request: Request):
    """Handle task-update broadcasts for cross-client real-time propagation."""
    event = await request.json()
    data = event.get("data", {})
    user_id = data.get("userId", "")
    event_data = data.get("data", {})

    action = event_data.get("action", "")
    task = event_data.get("task")
    task_title = task.get("title", "Task") if task else "Task"

    if action in ("created", "completed", "deleted"):
        try:
            action_text = {
                "created": "New task created",
                "completed": "Task completed",
                "deleted": "Task deleted",
            }.get(action, "Task updated")

            await push_service.send_to_user(
                user_id,
                title=f"{action_text}: {task_title}",
                body=f"Your task '{task_title}' was {action}.",
                url="/dashboard",
            )
        except Exception as e:
            logger.warning(f"Failed to send task update notification: {e}")

    return {"status": "SUCCESS"}
