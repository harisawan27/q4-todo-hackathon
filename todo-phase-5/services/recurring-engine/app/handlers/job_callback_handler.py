"""Dapr Jobs API callback handler for scheduled job execution."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Request

from app.services import job_service, pubsub_service, state_service
from app.services.recurrence_service import calculate_next_occurrence

logger = logging.getLogger("recurring-engine")

router = APIRouter(tags=["Jobs"])


@router.put("/job/{job_name}")
async def handle_job_callback(job_name: str, request: Request):
    """Handle Dapr Jobs API callback when a scheduled job fires."""
    payload = await request.json()
    job_data = payload.get("data", {})
    job_type = job_data.get("type", "")

    logger.info(f"Job callback received: {job_name} (type: {job_type})")

    # Idempotency check
    instance_id = f"{job_name}--{datetime.now(timezone.utc).strftime('%Y%m%d%H')}"
    if await state_service.check_idempotency(instance_id):
        logger.info(f"Duplicate job callback for {job_name}, skipping")
        return {"status": "ok"}

    try:
        if job_type == "recurrence-trigger":
            await _handle_recurrence_trigger(job_data)
        elif job_type == "reminder-fired":
            await _handle_reminder_fired(job_data)
        else:
            logger.warning(f"Unknown job type: {job_type}")

        await state_service.save_idempotency_marker(instance_id)
    except Exception as e:
        logger.error(f"Job callback error for {job_name}: {e}", exc_info=True)

    return {"status": "ok"}


async def _handle_recurrence_trigger(data: dict[str, Any]) -> None:
    """Handle a recurrence trigger — evaluate rule and generate next instance."""
    task_id = data.get("taskId", "")
    user_id = data.get("userId", "")

    from app import dapr_client

    index_data, _ = await dapr_client.get_state(f"recurrence-index--{task_id}")
    if not index_data:
        logger.warning(f"No recurrence index for task {task_id}")
        return

    rule_id = index_data.get("rule_id", "")
    rule = await state_service.get_recurrence_rule(rule_id)
    if rule is None or not rule.is_active:
        return

    next_date = calculate_next_occurrence(rule)
    if next_date is None:
        rule.is_active = False
        await state_service.save_recurrence_rule(rule)
        await job_service.cancel_job(f"recurrence-{task_id}")
        return

    new_task_id = str(uuid.uuid4())
    rule.instances_generated += 1
    await state_service.save_recurrence_rule(rule)

    event_data = {
        "eventId": str(uuid.uuid4()),
        "eventType": "task-recurrence-generated",
        "taskId": new_task_id,
        "parentTaskId": task_id,
        "userId": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "title": f"Recurring: {task_id}",
            "status": "pending",
            "dueDate": next_date.isoformat(),
            "recurrenceRule": {
                "frequency": rule.frequency.value,
                "timeOfDay": rule.time_of_day,
                "timezone": rule.timezone,
            },
            "instanceNumber": rule.instances_generated,
            "etag": None,
        },
    }
    await pubsub_service.publish_task_event(
        "task.recurrence-generated", event_data, task_id=new_task_id
    )
    logger.info(f"Recurrence trigger: generated {new_task_id} for {task_id}")


async def _handle_reminder_fired(data: dict[str, Any]) -> None:
    """Handle a reminder fired — publish to reminders topic."""
    task_id = data.get("taskId", "")
    user_id = data.get("userId", "")

    reminder_event = {
        "eventId": str(uuid.uuid4()),
        "eventType": "reminder-fired",
        "taskId": task_id,
        "userId": user_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": {
            "taskTitle": f"Task {task_id}",
            "dueDate": datetime.now(timezone.utc).isoformat(),
            "reminderType": "due-date",
            "reminderLevel": "30-minutes-before",
            "notificationChannel": "browser-push",
        },
    }
    await pubsub_service.publish_reminder_event("fired", reminder_event)
    logger.info(f"Reminder fired for task {task_id}")
