"""Dapr State Management wrapper for recurring-engine."""

import logging
from datetime import datetime, timezone
from typing import Any, Optional

from app import dapr_client
from app.models.recurrence import RecurrenceRule

logger = logging.getLogger("recurring-engine")


async def save_recurrence_rule(rule: RecurrenceRule) -> None:
    """Save a recurrence rule to state store."""
    await dapr_client.save_state([{
        "key": f"recurrence-rule--{rule.id}",
        "value": rule.model_dump(mode="json"),
    }])
    # Also save reverse lookup index
    await dapr_client.save_state([{
        "key": f"recurrence-index--{rule.task_id}",
        "value": {"rule_id": rule.id},
    }])


async def get_recurrence_rule(rule_id: str) -> Optional[RecurrenceRule]:
    """Get a recurrence rule by ID."""
    data, _ = await dapr_client.get_state(f"recurrence-rule--{rule_id}")
    if data is None:
        return None
    return RecurrenceRule(**data)


async def save_reminder(reminder_data: dict[str, Any]) -> None:
    """Save a reminder record."""
    reminder_id = reminder_data["id"]
    await dapr_client.save_state([{
        "key": f"reminder--{reminder_id}",
        "value": reminder_data,
    }])


async def get_reminder(reminder_id: str) -> Optional[dict[str, Any]]:
    """Get a reminder record."""
    data, _ = await dapr_client.get_state(f"reminder--{reminder_id}")
    return data


async def save_idempotency_marker(key: str) -> None:
    """Save an idempotency marker with 24h TTL."""
    await dapr_client.save_state([{
        "key": f"job-processed--{key}",
        "value": {"processedAt": datetime.now(timezone.utc).isoformat()},
        "metadata": {"ttlInSeconds": "86400"},
    }])


async def check_idempotency(key: str) -> bool:
    """Check if a job has already been processed."""
    data, _ = await dapr_client.get_state(f"job-processed--{key}")
    return data is not None
