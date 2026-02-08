"""Dapr event handlers for task lifecycle events."""

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Request

from app.services import job_service, pubsub_service, state_service
from app.services.recurrence_service import calculate_next_occurrence

logger = logging.getLogger("recurring-engine")

router = APIRouter(tags=["Events"])


@router.post("/events/task-created")
async def handle_task_created(request: Request):
    """Handle task-created events — register reminder if task has due_date."""
    event = await request.json()
    data = event.get("data", {})
    task_data = data.get("data", {})
    task_id = data.get("taskId", "")
    user_id = data.get("userId", "")

    due_date = task_data.get("dueDate")
    if due_date:
        try:
            due_time = task_data.get("dueTime")
            reminder_time = job_service.calculate_reminder_time(due_date, due_time)
            job_name = await job_service.register_reminder_job(task_id, reminder_time, user_id)

            reminder_data = {
                "id": str(uuid.uuid4()),
                "task_id": task_id,
                "user_id": user_id,
                "trigger_time": reminder_time.isoformat(),
                "reminder_level": "30-minutes-before",
                "status": "scheduled",
                "job_name": job_name,
                "notification_channel": "browser-push",
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            await state_service.save_reminder(reminder_data)
            logger.info(f"Registered reminder for task {task_id} at {reminder_time}")
        except Exception as e:
            logger.error(f"Failed to register reminder for task {task_id}: {e}")

    # Handle recurrence rule if present
    recurrence_rule = task_data.get("recurrenceRule")
    if recurrence_rule:
        try:
            from app.models.recurrence import RecurrenceRule

            rule = RecurrenceRule(
                task_id=task_id,
                user_id=user_id,
                **recurrence_rule,
            )
            await state_service.save_recurrence_rule(rule)

            cron = job_service.recurrence_to_cron(
                frequency=rule.frequency.value,
                interval=rule.interval,
                time_of_day=rule.time_of_day,
                days_of_week=rule.days_of_week,
                day_of_month=rule.day_of_month,
                cron_expression=rule.cron_expression,
            )
            job_name = await job_service.register_recurring_job(task_id, cron, user_id)
            rule.job_name = job_name
            await state_service.save_recurrence_rule(rule)
            logger.info(f"Registered recurrence for task {task_id}: {rule.frequency}")
        except Exception as e:
            logger.error(f"Failed to register recurrence for task {task_id}: {e}")

    return {"status": "SUCCESS"}


@router.post("/events/task-completed")
async def handle_task_completed(request: Request):
    """Handle task-completed — generate next instance if recurring."""
    event = await request.json()
    data = event.get("data", {})
    task_data = data.get("data", {})
    task_id = data.get("taskId", "")
    user_id = data.get("userId", "")

    has_recurrence = task_data.get("hasRecurrence", False)
    if not has_recurrence:
        return {"status": "SUCCESS"}

    # Idempotency check
    idempotency_key = f"{task_id}--completed"
    if await state_service.check_idempotency(idempotency_key):
        logger.info(f"Duplicate task-completed for {task_id}, skipping")
        return {"status": "SUCCESS"}

    try:
        from app import dapr_client

        index_data, _ = await dapr_client.get_state(f"recurrence-index--{task_id}")
        if not index_data:
            logger.warning(f"No recurrence rule found for task {task_id}")
            return {"status": "SUCCESS"}

        rule_id = index_data.get("rule_id", "")
        rule = await state_service.get_recurrence_rule(rule_id)
        if rule is None or not rule.is_active:
            return {"status": "SUCCESS"}

        next_date = calculate_next_occurrence(rule)
        if next_date is None:
            logger.info(f"Recurrence ended for task {task_id}")
            rule.is_active = False
            await state_service.save_recurrence_rule(rule)
            return {"status": "SUCCESS"}

        new_task_id = str(uuid.uuid4())
        rule.instances_generated += 1
        await state_service.save_recurrence_rule(rule)

        new_event_data = {
            "eventId": str(uuid.uuid4()),
            "eventType": "task-recurrence-generated",
            "taskId": new_task_id,
            "parentTaskId": task_id,
            "userId": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {
                "title": task_data.get("title", "Recurring Task"),
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
            "task.recurrence-generated", new_event_data, task_id=new_task_id
        )

        await state_service.save_idempotency_marker(idempotency_key)
        logger.info(f"Generated next recurring instance {new_task_id} for task {task_id}, due {next_date}")

    except Exception as e:
        logger.error(f"Failed to generate next recurring instance for {task_id}: {e}")
        return {"status": "RETRY"}

    return {"status": "SUCCESS"}


@router.post("/events/task-updated")
async def handle_task_updated(request: Request):
    """Handle task-updated — update reminder if due_date changed."""
    event = await request.json()
    data = event.get("data", {})
    task_data = data.get("data", {})
    task_id = data.get("taskId", "")
    user_id = data.get("userId", "")

    changed_fields = task_data.get("changedFields", [])
    if "due_date" not in changed_fields and "due_time" not in changed_fields:
        return {"status": "SUCCESS"}

    try:
        await job_service.cancel_job(f"reminder-{task_id}")
    except Exception:
        pass

    new_due_date = task_data.get("after", {}).get("due_date")
    if new_due_date:
        try:
            new_due_time = task_data.get("after", {}).get("due_time")
            reminder_time = job_service.calculate_reminder_time(new_due_date, new_due_time)
            await job_service.register_reminder_job(task_id, reminder_time, user_id)
            logger.info(f"Updated reminder for task {task_id}")
        except Exception as e:
            logger.error(f"Failed to update reminder for task {task_id}: {e}")

    return {"status": "SUCCESS"}


@router.post("/events/task-deleted")
async def handle_task_deleted(request: Request):
    """Handle task-deleted — cancel any associated jobs."""
    event = await request.json()
    data = event.get("data", {})
    task_id = data.get("taskId", "")

    try:
        await job_service.cancel_job(f"reminder-{task_id}")
    except Exception:
        pass

    try:
        await job_service.cancel_job(f"recurrence-{task_id}")
    except Exception:
        pass

    logger.info(f"Cancelled jobs for deleted task {task_id}")
    return {"status": "SUCCESS"}


@router.post("/events/task-events")
async def handle_task_events_default(request: Request):
    """Default handler for unmatched task events."""
    return {"status": "SUCCESS"}
