"""Notification CRUD endpoints with Duolingo-style deadline reminders"""

import logging
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status, BackgroundTasks
from sqlmodel import Session, select, func

from app.auth.jwt_bearer import CurrentUser, get_current_user
from app.database import get_session
from app.models.notification import (
    Notification,
    NotificationRead,
    NotificationUpdate,
)
from app.services.scheduler import scheduler_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])


@router.get("", response_model=list[NotificationRead])
async def list_notifications(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
    unread_only: bool = Query(False, description="Filter to unread notifications only"),
    limit: int = Query(50, ge=1, le=100, description="Max notifications to return"),
) -> list[Notification]:
    """List notifications for the authenticated user, ordered by created_at DESC"""
    statement = select(Notification).where(
        Notification.user_id == current_user.user_id
    )

    if unread_only:
        statement = statement.where(Notification.read == False)

    statement = statement.order_by(Notification.created_at.desc()).limit(limit)
    notifications = session.exec(statement).all()
    return list(notifications)


@router.get("/unread-count")
async def get_unread_count(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """Get count of unread notifications"""
    statement = select(func.count(Notification.id)).where(
        Notification.user_id == current_user.user_id,
        Notification.read == False
    )
    count = session.exec(statement).first() or 0
    return {"unread_count": count}


@router.get("/{notification_id}", response_model=NotificationRead)
async def get_notification(
    notification_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Notification:
    """Get a specific notification by ID"""
    statement = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.user_id
    )
    notification = session.exec(statement).first()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    return notification


@router.patch("/{notification_id}", response_model=NotificationRead)
async def update_notification(
    notification_id: str,
    update_data: NotificationUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Notification:
    """Update a notification (mark as read)"""
    statement = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.user_id
    )
    notification = session.exec(statement).first()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if update_data.read is not None:
        notification.read = update_data.read

    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.post("/mark-all-read", status_code=status.HTTP_200_OK)
async def mark_all_as_read(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """Mark all notifications as read for the authenticated user"""
    statement = select(Notification).where(
        Notification.user_id == current_user.user_id,
        Notification.read == False
    )
    notifications = session.exec(statement).all()

    count = 0
    for notification in notifications:
        notification.read = True
        session.add(notification)
        count += 1

    session.commit()
    return {"marked_read": count}


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> None:
    """Delete a notification"""
    statement = select(Notification).where(
        Notification.id == notification_id,
        Notification.user_id == current_user.user_id
    )
    notification = session.exec(statement).first()
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    session.delete(notification)
    session.commit()


@router.delete("", status_code=status.HTTP_200_OK)
async def clear_all_notifications(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
    read_only: bool = Query(False, description="Only clear read notifications"),
) -> dict:
    """Clear all notifications for the authenticated user"""
    statement = select(Notification).where(
        Notification.user_id == current_user.user_id
    )

    if read_only:
        statement = statement.where(Notification.read == True)

    notifications = session.exec(statement).all()

    count = 0
    for notification in notifications:
        session.delete(notification)
        count += 1

    session.commit()
    return {"deleted": count}


@router.post("/check-deadlines", status_code=status.HTTP_200_OK)
async def check_deadlines_now(
    background_tasks: BackgroundTasks,
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """
    Trigger an immediate deadline check for all users.

    This endpoint allows real-time triggering of the deadline reminder system.
    The check runs in the background and will send notifications/emails for
    any tasks that have crossed reminder thresholds.

    Duolingo-style reminders are sent at:
    - 1 day (24 hours) before deadline
    - 12 hours before deadline
    - 6 hours before deadline
    - 3 hours before deadline
    - 1 hour before deadline
    - When overdue

    Reminders stop automatically when a task is marked as completed.
    """
    logger.info(f"Manual deadline check triggered by user {current_user.user_id}")

    # Run the check in background to not block the response
    background_tasks.add_task(scheduler_service.check_upcoming_deadlines)

    return {
        "status": "triggered",
        "message": "Deadline check initiated. New notifications will appear shortly.",
        "reminder_intervals": ["24h", "12h", "6h", "3h", "1h", "overdue"]
    }


@router.get("/reminder-schedule")
async def get_reminder_schedule(
    current_user: CurrentUser = Depends(get_current_user),
) -> dict:
    """
    Get the Duolingo-style reminder schedule configuration.

    Returns the intervals at which deadline reminders are sent.
    This helps the frontend display reminder timing information to users.
    """
    return {
        "schedule": [
            {"level": "day_before", "hours_before": 24, "label": "1 day before", "urgency": "medium"},
            {"level": "hours_12", "hours_before": 12, "label": "12 hours before", "urgency": "medium"},
            {"level": "hours_6", "hours_before": 6, "label": "6 hours before", "urgency": "high"},
            {"level": "hours_3", "hours_before": 3, "label": "3 hours before", "urgency": "high"},
            {"level": "hours_1", "hours_before": 1, "label": "1 hour before", "urgency": "critical"},
            {"level": "overdue", "hours_before": 0, "label": "Overdue", "urgency": "critical"},
        ],
        "behavior": {
            "stops_on_completion": True,
            "check_interval_minutes": 5,
            "email_enabled": True,
            "in_app_notifications": True,
        },
        "message": "Reminders are sent at each interval until the task is marked complete - just like Duolingo!"
    }
