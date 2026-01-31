"""Notification service for creating and managing notifications"""

import logging
from typing import Optional
from sqlmodel import Session

from app.models.notification import Notification, NotificationType
from app.models.task import Task
from app.services.webpush import webpush_service
from app.services.fcm import fcm_service

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for creating notifications"""

    @staticmethod
    def create_notification(
        session: Session,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType,
        task_id: Optional[str] = None,
    ) -> Notification:
        """Create a new notification and send push notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            type=notification_type.value,
            task_id=task_id,
        )
        session.add(notification)
        session.commit()
        session.refresh(notification)
        logger.info(f"Created notification: {title} for user {user_id}")

        # Send Web Push notification to all user's devices (browser)
        try:
            push_count = webpush_service.send_to_user(session, user_id, notification)
            if push_count > 0:
                logger.info(f"Sent Web Push notification to {push_count} device(s)")
        except Exception as e:
            logger.error(f"Failed to send Web Push notification: {e}")

        # Send FCM notification to all user's devices (native apps)
        try:
            fcm_count = fcm_service.send_to_user(session, user_id, notification)
            if fcm_count > 0:
                logger.info(f"Sent FCM notification to {fcm_count} device(s)")
        except Exception as e:
            logger.error(f"Failed to send FCM notification: {e}")

        return notification

    @staticmethod
    def notify_task_created(session: Session, task: Task) -> Notification:
        """Create notification when a task is created"""
        return NotificationService.create_notification(
            session=session,
            user_id=task.user_id,
            title="Task Created",
            message=f"New task '{task.title}' has been created.",
            notification_type=NotificationType.TASK_CREATED,
            task_id=task.id,
        )

    @staticmethod
    def notify_task_completed(session: Session, task: Task) -> Notification:
        """Create notification when a task is completed"""
        return NotificationService.create_notification(
            session=session,
            user_id=task.user_id,
            title="Task Completed",
            message=f"You completed '{task.title}'. Great job!",
            notification_type=NotificationType.TASK_COMPLETED,
            task_id=task.id,
        )

    @staticmethod
    def notify_task_deleted(session: Session, user_id: str, task_title: str, task_id: str) -> Notification:
        """Create notification when a task is deleted"""
        return NotificationService.create_notification(
            session=session,
            user_id=user_id,
            title="Task Deleted",
            message=f"Task '{task_title}' has been deleted.",
            notification_type=NotificationType.TASK_DELETED,
            task_id=task_id,
        )

    @staticmethod
    def notify_deadline_approaching(
        session: Session,
        task: Task,
        hours_remaining: int,
    ) -> Notification:
        """Create notification when a task deadline is approaching"""
        if hours_remaining <= 0:
            message = f"Task '{task.title}' deadline has passed!"
            title = "Deadline Passed"
            notification_type = NotificationType.DEADLINE_PASSED
        elif hours_remaining <= 1:
            message = f"Task '{task.title}' is due in less than an hour!"
            title = "Deadline Imminent"
            notification_type = NotificationType.DEADLINE_APPROACHING
        elif hours_remaining <= 24:
            message = f"Task '{task.title}' is due in {hours_remaining} hours."
            title = "Deadline Approaching"
            notification_type = NotificationType.DEADLINE_APPROACHING
        else:
            days = hours_remaining // 24
            message = f"Task '{task.title}' is due in {days} day(s)."
            title = "Upcoming Deadline"
            notification_type = NotificationType.DEADLINE_APPROACHING

        return NotificationService.create_notification(
            session=session,
            user_id=task.user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            task_id=task.id,
        )


# Singleton instance
notification_service = NotificationService()
