"""Dapr event handlers for reminder events — delivers push notifications."""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.models.notification import Notification, NotificationType
from app.services import push_service, state_service

logger = logging.getLogger("notification-service")

router = APIRouter(tags=["Events"])


@router.post("/events/reminder-fired")
async def handle_reminder_fired(request: Request):
    """Handle reminder-fired events — deliver push notification."""
    event = await request.json()
    data = event.get("data", {})
    event_data = data.get("data", {})
    user_id = data.get("userId", "")
    task_id = data.get("taskId", "")

    task_title = event_data.get("taskTitle", "Task")
    reminder_level = event_data.get("reminderLevel", "30-minutes-before")

    try:
        title = f"Reminder: {task_title}"
        body = f"Due {reminder_level.replace('-', ' ')}"
        url = f"/dashboard/tasks/{task_id}"

        sent_count = await push_service.send_to_user(user_id, title, body, url)

        notification = Notification(
            user_id=user_id,
            title=title,
            message=body,
            type=NotificationType.DEADLINE_APPROACHING,
            task_id=task_id,
            reminder_level=reminder_level,
            delivered=sent_count > 0,
            delivered_at=datetime.now(timezone.utc) if sent_count > 0 else None,
        )
        await state_service.save_notification(notification)

        logger.info(f"Reminder delivered for task {task_id}: {sent_count} notifications sent")
        return {"status": "SUCCESS"}

    except Exception as e:
        logger.error(f"Failed to deliver reminder for task {task_id}: {e}")
        return {"status": "RETRY"}


@router.post("/events/recurring-trigger")
async def handle_recurring_trigger(request: Request):
    """Handle recurring-trigger events — notify user of new recurring instance."""
    event = await request.json()
    data = event.get("data", {})
    event_data = data.get("data", {})
    user_id = data.get("userId", "")
    task_id = data.get("taskId", "")

    task_title = event_data.get("taskTitle", "Recurring Task")

    try:
        title = f"Recurring: {task_title}"
        body = "A new instance of your recurring task has been created"
        url = f"/dashboard/tasks/{task_id}"

        await push_service.send_to_user(user_id, title, body, url)

        notification = Notification(
            user_id=user_id,
            title=title,
            message=body,
            type=NotificationType.RECURRENCE_GENERATED,
            task_id=task_id,
        )
        await state_service.save_notification(notification)

        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error(f"Failed to deliver recurring trigger notification: {e}")
        return {"status": "RETRY"}


@router.post("/events/reminders")
async def handle_reminders_default(request: Request):
    """Default handler for unmatched reminder events."""
    return {"status": "SUCCESS"}
