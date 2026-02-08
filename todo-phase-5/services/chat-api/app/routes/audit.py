"""Audit trail endpoints and Dapr event handler for task-events consumption."""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.middleware.auth import get_current_user
from app.models.audit import AuditRecord
from app.services import audit_service

logger = logging.getLogger("chat-api")

router = APIRouter(tags=["Audit"])


@router.get("/tasks/{task_id}/audit", response_model=list[AuditRecord])
async def get_task_audit_trail(
    task_id: str,
    user_id: str = Depends(get_current_user),
):
    """Get the full audit trail for a task."""
    records = await audit_service.get_task_audit_trail(task_id)
    if not records:
        return []
    # Filter to only show records for the authenticated user
    return [r for r in records if r.user_id == user_id]


@router.post("/events/audit-task-events")
async def handle_audit_task_events(request: Request):
    """Dapr subscription handler — consumes task-events for audit recording."""
    event = await request.json()
    data = event.get("data", {})

    event_id = data.get("eventId", data.get("event_id", ""))
    event_type = data.get("eventType", data.get("event_type", ""))
    task_id = data.get("taskId", data.get("task_id", ""))
    user_id = data.get("userId", data.get("user_id", ""))
    timestamp = data.get("timestamp", "")
    event_data = data.get("data", {})

    if not task_id or not event_type:
        logger.warning(f"Audit handler: missing task_id or event_type in event")
        return {"status": "SUCCESS"}

    try:
        await audit_service.record_audit(
            event_id=event_id,
            event_type=event_type,
            task_id=task_id,
            user_id=user_id,
            timestamp=timestamp,
            data=event_data,
        )
        return {"status": "SUCCESS"}
    except Exception as e:
        logger.error(f"Failed to record audit: {e}")
        return {"status": "RETRY"}
