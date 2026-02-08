"""Dapr Jobs API wrapper for scheduling recurring tasks and reminders."""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from app import dapr_client

logger = logging.getLogger("recurring-engine")


async def register_recurring_job(task_id: str, cron_schedule: str, user_id: str) -> str:
    """Register a recurring job with the Dapr Jobs API."""
    job_name = f"recurrence-{task_id}"
    job_config = {
        "schedule": cron_schedule,
        "repeats": 0,
        "data": {
            "taskId": task_id,
            "type": "recurrence-trigger",
            "userId": user_id,
        },
    }
    await dapr_client.register_job(job_name, job_config)
    logger.info(f"Registered recurring job: {job_name} with schedule {cron_schedule}")
    return job_name


async def register_reminder_job(task_id: str, trigger_time: datetime, user_id: str) -> str:
    """Register a one-shot reminder job."""
    job_name = f"reminder-{task_id}"
    job_config = {
        "dueTime": trigger_time.isoformat(),
        "repeats": 1,
        "data": {
            "taskId": task_id,
            "type": "reminder-fired",
            "userId": user_id,
        },
    }
    await dapr_client.register_job(job_name, job_config)
    logger.info(f"Registered reminder job: {job_name} at {trigger_time.isoformat()}")
    return job_name


async def cancel_job(job_name: str) -> None:
    """Cancel a scheduled job."""
    try:
        await dapr_client.delete_job(job_name)
        logger.info(f"Cancelled job: {job_name}")
    except Exception as e:
        logger.warning(f"Failed to cancel job {job_name}: {e}")


async def get_job_status(job_name: str) -> Optional[dict[str, Any]]:
    """Get the status of a scheduled job."""
    return await dapr_client.get_job(job_name)


def calculate_reminder_time(due_date: str, due_time: str | None = None) -> datetime:
    """Calculate when to fire a reminder (30 minutes before due)."""
    if due_time:
        dt = datetime.fromisoformat(f"{due_date}T{due_time}")
    else:
        dt = datetime.fromisoformat(f"{due_date}T09:00:00")

    dt = dt.replace(tzinfo=timezone.utc)
    reminder_time = dt - timedelta(minutes=30)

    now = datetime.now(timezone.utc)
    if reminder_time <= now:
        return now + timedelta(minutes=1)

    return reminder_time


def recurrence_to_cron(
    frequency: str,
    interval: int = 1,
    time_of_day: str = "09:00",
    days_of_week: list[int] | None = None,
    day_of_month: int | None = None,
    cron_expression: str | None = None,
) -> str:
    """Convert a recurrence frequency to a cron schedule string."""
    if cron_expression:
        return cron_expression

    hour, minute = time_of_day.split(":")

    if frequency == "daily":
        if interval == 1:
            return f"{minute} {hour} * * *"
        return f"@every {24 * interval}h"

    if frequency == "weekly":
        if days_of_week:
            cron_days = ",".join(str((d + 1) % 7) for d in days_of_week)
            return f"{minute} {hour} * * {cron_days}"
        return f"{minute} {hour} * * 1"

    if frequency == "weekday":
        return f"{minute} {hour} * * 1-5"

    if frequency == "monthly":
        dom = day_of_month or 1
        return f"{minute} {hour} {dom} * *"

    return f"{minute} {hour} * * *"
