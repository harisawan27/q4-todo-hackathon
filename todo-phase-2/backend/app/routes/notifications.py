"""Notification CRUD endpoints"""

from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select, func

from app.auth.jwt_bearer import CurrentUser, get_current_user
from app.database import get_session
from app.models.notification import (
    Notification,
    NotificationRead,
    NotificationUpdate,
)

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
