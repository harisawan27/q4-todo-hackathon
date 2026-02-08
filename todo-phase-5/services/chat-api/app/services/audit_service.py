"""Audit trail service for recording task lifecycle events."""

import logging
from datetime import datetime, timezone
from typing import Optional

from app import dapr_client
from app.models.audit import AuditAction, AuditIndex, AuditRecord

logger = logging.getLogger("chat-api")

EVENT_TYPE_TO_ACTION = {
    "task-created": AuditAction.CREATED,
    "task-updated": AuditAction.UPDATED,
    "task-completed": AuditAction.COMPLETED,
    "task-deleted": AuditAction.DELETED,
    "task-recurrence-generated": AuditAction.RECURRENCE_GENERATED,
}


async def record_audit(
    event_id: str,
    event_type: str,
    task_id: str,
    user_id: str,
    timestamp: str,
    data: dict,
) -> AuditRecord:
    """Create and persist an audit record from a task event."""
    action = EVENT_TYPE_TO_ACTION.get(event_type, AuditAction.CREATED)

    change_summary = _build_change_summary(action, data)

    record = AuditRecord(
        event_id=event_id,
        task_id=task_id,
        user_id=user_id,
        action=action,
        timestamp=datetime.fromisoformat(timestamp) if timestamp else datetime.now(timezone.utc),
        change_summary=change_summary,
        before_state=data.get("before"),
        after_state=data.get("after"),
    )

    # Save audit record
    record_key = f"audit--{record.id}"
    await dapr_client.save_state([{
        "key": record_key,
        "value": record.model_dump(mode="json"),
    }])

    # Update task audit index
    index_key = f"audit-index--{task_id}"
    index_data, _ = await dapr_client.get_state(index_key)
    if index_data:
        audit_index = AuditIndex(**index_data)
    else:
        audit_index = AuditIndex(task_id=task_id)

    audit_index.record_ids.append(record.id)
    await dapr_client.save_state([{
        "key": index_key,
        "value": audit_index.model_dump(mode="json"),
    }])

    logger.info(f"Audit recorded: {action.value} for task {task_id}")
    return record


async def get_task_audit_trail(task_id: str) -> list[AuditRecord]:
    """Retrieve the full audit trail for a task."""
    index_data, _ = await dapr_client.get_state(f"audit-index--{task_id}")
    if not index_data:
        return []

    audit_index = AuditIndex(**index_data)
    if not audit_index.record_ids:
        return []

    keys = [f"audit--{rid}" for rid in audit_index.record_ids]
    bulk_results = await dapr_client.bulk_get_state(keys)

    records = []
    for item in bulk_results:
        if item.get("data"):
            try:
                records.append(AuditRecord(**item["data"]))
            except Exception as e:
                logger.warning(f"Failed to parse audit record: {e}")

    return sorted(records, key=lambda r: r.timestamp, reverse=True)


def _build_change_summary(action: AuditAction, data: dict) -> str:
    """Build a human-readable change summary."""
    if action == AuditAction.CREATED:
        title = data.get("title", "Unknown")
        return f"Task '{title}' created"
    elif action == AuditAction.UPDATED:
        fields = data.get("changedFields", [])
        return f"Task updated: {', '.join(fields)}" if fields else "Task updated"
    elif action == AuditAction.COMPLETED:
        title = data.get("title", "Unknown")
        return f"Task '{title}' completed"
    elif action == AuditAction.DELETED:
        title = data.get("title", "Unknown")
        return f"Task '{title}' deleted"
    elif action == AuditAction.RECURRENCE_GENERATED:
        title = data.get("title", "Unknown")
        instance = data.get("instanceNumber", "?")
        return f"Recurring instance #{instance} of '{title}' generated"
    return "Unknown action"
