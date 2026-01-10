"""Background job scheduler for deadline reminders"""

import logging
from datetime import datetime, timezone, timedelta, date
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session, select

from app.config import get_settings
from app.database import engine
from app.models.task import Task
from app.models.notification import Notification, NotificationType
from app.services.notification import NotificationService

logger = logging.getLogger(__name__)


class SchedulerService:
    """Background scheduler service for deadline reminders"""

    def __init__(self):
        self.settings = get_settings()
        self.scheduler: Optional[BackgroundScheduler] = None

    def start(self):
        """Start the background scheduler"""
        if not self.settings.scheduler_enabled:
            logger.info("Scheduler is disabled in settings")
            return

        if self.scheduler is not None:
            logger.warning("Scheduler already running")
            return

        self.scheduler = BackgroundScheduler()

        # Check deadlines every hour
        self.scheduler.add_job(
            self.check_upcoming_deadlines,
            trigger=IntervalTrigger(hours=1),
            id="check_deadlines",
            name="Check upcoming deadlines",
            replace_existing=True,
        )

        # Also run immediately on startup
        self.scheduler.add_job(
            self.check_upcoming_deadlines,
            id="check_deadlines_startup",
            name="Initial deadline check",
            replace_existing=True,
        )

        self.scheduler.start()
        logger.info("Background scheduler started")

    def stop(self):
        """Stop the background scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None
            logger.info("Background scheduler stopped")

    def check_upcoming_deadlines(self):
        """Check for tasks with upcoming deadlines and send reminders"""
        logger.info("Checking for upcoming deadlines...")

        try:
            with Session(engine) as session:
                # Get current date/time
                now = datetime.now(timezone.utc)
                today = now.date()

                # Calculate the reminder window
                reminder_hours = self.settings.deadline_reminder_hours
                reminder_window = today + timedelta(hours=reminder_hours)

                # Find tasks with due dates within the reminder window
                # that haven't had notifications sent yet
                statement = select(Task).where(
                    Task.due_date != None,
                    Task.due_date <= reminder_window,
                    Task.completed == False,
                )

                tasks = session.exec(statement).all()
                logger.info(f"Found {len(tasks)} tasks with upcoming deadlines")

                for task in tasks:
                    self._process_deadline_reminder(session, task, today)

        except Exception as e:
            logger.error(f"Error checking deadlines: {e}")

    def _process_deadline_reminder(
        self, session: Session, task: Task, today: date
    ):
        """Process deadline reminder for a single task"""
        try:
            if task.due_date is None:
                return

            # Check if we've already sent a notification for this task today
            existing_notification = session.exec(
                select(Notification).where(
                    Notification.task_id == task.id,
                    Notification.type.in_([
                        NotificationType.DEADLINE_APPROACHING.value,
                        NotificationType.DEADLINE_PASSED.value,
                    ]),
                    Notification.created_at >= datetime.combine(
                        today, datetime.min.time()
                    ).replace(tzinfo=timezone.utc)
                )
            ).first()

            if existing_notification:
                logger.debug(f"Already notified for task {task.id} today")
                return

            # Calculate hours until deadline
            due_datetime = datetime.combine(
                task.due_date, datetime.max.time()
            ).replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            time_diff = due_datetime - now
            hours_remaining = int(time_diff.total_seconds() / 3600)

            # Create notification
            NotificationService.notify_deadline_approaching(
                session=session,
                task=task,
                hours_remaining=hours_remaining,
            )

            logger.info(
                f"Created deadline notification for task '{task.title}' "
                f"(due: {task.due_date}, hours remaining: {hours_remaining})"
            )

        except Exception as e:
            logger.error(f"Error processing deadline for task {task.id}: {e}")


# Singleton instance
scheduler_service = SchedulerService()
