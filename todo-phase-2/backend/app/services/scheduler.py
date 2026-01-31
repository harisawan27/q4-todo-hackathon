"""Background job scheduler for Duolingo-style deadline reminders"""

import logging
from datetime import datetime, timezone, timedelta, time
from typing import Optional, List, Tuple

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlmodel import Session, select

from app.config import get_settings
from app.database import engine
from app.models.task import Task
from app.models.notification import (
    Notification,
    NotificationType,
    ReminderLevel,
    REMINDER_SCHEDULE,
)
from app.services.notification import NotificationService
from app.services.email import email_service

logger = logging.getLogger(__name__)


# Urgency messages for each reminder level (Duolingo-style)
# These messages are motivational and progressively urgent
REMINDER_MESSAGES = {
    ReminderLevel.DAY_BEFORE: {
        "title": "1 Day Left!",
        "message": "Your task '{task}' is due tomorrow. Stay on track!",
        "email_subject": "Reminder: '{task}' is due in 24 hours!",
        "urgency": "medium",
        "emoji": "📅",
        "motivational": "Plan ahead to avoid last-minute rush!",
    },
    ReminderLevel.HOURS_12: {
        "title": "12 Hours Left!",
        "message": "Half a day left to complete '{task}'. You've got this!",
        "email_subject": "12 hours left: '{task}' deadline approaching",
        "urgency": "medium",
        "emoji": "⏰",
        "motivational": "Great time to knock this out!",
    },
    ReminderLevel.HOURS_6: {
        "title": "6 Hours Remaining!",
        "message": "'{task}' is due in 6 hours. Time to focus and finish!",
        "email_subject": "6 hours remaining: Don't forget '{task}'",
        "urgency": "high",
        "emoji": "⚠️",
        "motivational": "You're almost there - push through!",
    },
    ReminderLevel.HOURS_3: {
        "title": "3 Hours to Go!",
        "message": "Hurry! '{task}' is due in just 3 hours!",
        "email_subject": "Urgent: Only 3 hours left for '{task}'",
        "urgency": "high",
        "emoji": "🔥",
        "motivational": "Crunch time - you can do this!",
    },
    ReminderLevel.HOURS_1: {
        "title": "Final Hour!",
        "message": "Last chance! '{task}' is due in 1 hour. Complete it now!",
        "email_subject": "FINAL HOUR: '{task}' deadline imminent!",
        "urgency": "critical",
        "emoji": "🚨",
        "motivational": "One hour left - finish strong!",
    },
    ReminderLevel.OVERDUE: {
        "title": "Deadline Passed!",
        "message": "'{task}' is now overdue. Complete it as soon as possible!",
        "email_subject": "OVERDUE: '{task}' deadline has passed",
        "urgency": "critical",
        "emoji": "❌",
        "motivational": "Better late than never - get it done!",
    },
}


class SchedulerService:
    """Background scheduler service for Duolingo-style deadline reminders"""

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

        # Check deadlines every 5 minutes for near real-time reminders
        # This ensures users get timely notifications at each reminder threshold
        self.scheduler.add_job(
            self.check_upcoming_deadlines,
            trigger=IntervalTrigger(minutes=5),
            id="check_deadlines",
            name="Check upcoming deadlines (Duolingo-style)",
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
        logger.info("Duolingo-style reminder scheduler started (checking every 5 minutes)")

    def stop(self):
        """Stop the background scheduler"""
        if self.scheduler:
            self.scheduler.shutdown()
            self.scheduler = None
            logger.info("Background scheduler stopped")

    def check_upcoming_deadlines(self):
        """Check for tasks with upcoming deadlines and send tiered reminders"""
        logger.info("Checking for upcoming deadlines...")

        try:
            with Session(engine) as session:
                now = datetime.now(timezone.utc)

                # Find all incomplete tasks with due dates
                statement = select(Task).where(
                    Task.due_date != None,
                    Task.completed == False,
                )

                tasks = session.exec(statement).all()
                logger.info(f"Found {len(tasks)} incomplete tasks with due dates")

                for task in tasks:
                    self._process_task_reminders(session, task, now)

        except Exception as e:
            logger.error(f"Error checking deadlines: {e}")

    def _get_due_datetime(self, task: Task) -> datetime:
        """Get the full datetime of when a task is due"""
        if task.due_time:
            due_time = task.due_time
        else:
            # Default to end of day if no time specified
            due_time = time(23, 59, 59)

        return datetime.combine(
            task.due_date, due_time
        ).replace(tzinfo=timezone.utc)

    def _get_sent_reminder_levels(self, session: Session, task_id: str) -> List[str]:
        """Get all reminder levels already sent for a task"""
        statement = select(Notification.reminder_level).where(
            Notification.task_id == task_id,
            Notification.reminder_level != None,
        )
        results = session.exec(statement).all()
        return [r for r in results if r is not None]

    def _determine_reminder_level(self, hours_remaining: float) -> Optional[ReminderLevel]:
        """
        Determine which reminder level should be triggered based on hours remaining.
        Returns the highest priority (most urgent/closest to deadline) level that applies.

        We iterate through all thresholds and keep the last match, which will be
        the most specific one (smallest threshold that still applies).

        For example, if 6 hours remain:
        - 6 <= 24 (DAY_BEFORE) → matches, but continue
        - 6 <= 12 (HOURS_12) → matches, but continue
        - 6 <= 6 (HOURS_6) → matches, this is the final answer
        - 6 <= 3 (HOURS_3) → no match
        """
        matching_level = None
        for level, threshold_hours in REMINDER_SCHEDULE:
            if hours_remaining <= threshold_hours:
                matching_level = level
                # Continue iterating to find more specific (smaller threshold) match
        return matching_level

    def _process_task_reminders(self, session: Session, task: Task, now: datetime):
        """Process reminders for a single task using Duolingo-style tiered approach"""
        try:
            if task.due_date is None:
                return

            # Calculate time until deadline
            due_datetime = self._get_due_datetime(task)
            time_diff = due_datetime - now
            hours_remaining = time_diff.total_seconds() / 3600

            # Determine which reminder level should be triggered
            current_level = self._determine_reminder_level(hours_remaining)

            if current_level is None:
                # Not within any reminder window yet (more than 24 hours away)
                return

            # Check which reminders have already been sent
            sent_levels = self._get_sent_reminder_levels(session, task.id)

            if current_level.value in sent_levels:
                # Already sent this reminder level
                logger.debug(f"Already sent {current_level.value} reminder for task {task.id}")
                return

            # Send the reminder!
            self._send_reminder(session, task, current_level, hours_remaining)

        except Exception as e:
            logger.error(f"Error processing reminders for task {task.id}: {e}")

    def _send_reminder(
        self,
        session: Session,
        task: Task,
        level: ReminderLevel,
        hours_remaining: float
    ):
        """Send notification and email for a reminder level"""
        try:
            messages = REMINDER_MESSAGES[level]
            task_title = task.title

            # Create in-app notification
            notification_type = (
                NotificationType.DEADLINE_PASSED
                if level == ReminderLevel.OVERDUE
                else NotificationType.DEADLINE_APPROACHING
            )

            notification = Notification(
                user_id=task.user_id,
                title=messages["title"],
                message=messages["message"].format(task=task_title),
                type=notification_type.value,
                task_id=task.id,
                reminder_level=level.value,
            )
            session.add(notification)

            # Send email reminder
            email_sent = self._send_reminder_email(task, level, hours_remaining)

            if email_sent:
                notification.email_sent = True

            session.commit()

            due_str = f"{task.due_date}"
            if task.due_time:
                due_str += f" {task.due_time}"

            logger.info(
                f"Sent {level.value} reminder for task '{task_title}' "
                f"(due: {due_str}, hours remaining: {hours_remaining:.1f}, email: {email_sent})"
            )

        except Exception as e:
            logger.error(f"Error sending reminder for task {task.id}: {e}")
            session.rollback()

    def _send_reminder_email(
        self,
        task: Task,
        level: ReminderLevel,
        hours_remaining: float
    ) -> bool:
        """Send reminder email with urgency-appropriate styling"""
        try:
            # Check if email service is enabled
            if not email_service.enabled:
                logger.info(f"Email service disabled, skipping email for task {task.id}")
                return False

            # Get user email from auth system
            user_email = self._get_user_email(task.user_id)
            if not user_email:
                logger.warning(f"No email found for user {task.user_id}, skipping email reminder")
                return False

            messages = REMINDER_MESSAGES[level]
            urgency = messages["urgency"]

            logger.info(f"Sending {level.value} email reminder to {user_email} for task '{task.title}'")

            # Send urgency-styled email
            result = email_service.send_deadline_reminder_urgent(
                to_email=user_email,
                user_name=None,  # Could be fetched from user profile
                task_title=task.title,
                due_date=task.due_date,
                due_time=task.due_time,
                task_id=task.id,
                urgency=urgency,
                hours_remaining=hours_remaining,
                reminder_level=level,
            )

            if result:
                logger.info(f"Email sent successfully to {user_email}")
            else:
                logger.warning(f"Email sending returned False for {user_email}")

            return result

        except Exception as e:
            logger.error(f"Error sending reminder email for task {task.id}: {e}", exc_info=True)
            return False

    def _get_user_email(self, user_id: str) -> Optional[str]:
        """Get user email from the auth system (Better Auth user table)"""
        try:
            # Query the user table from Better Auth
            with Session(engine) as session:
                from sqlalchemy import text
                result = session.execute(
                    text('SELECT email FROM "user" WHERE id = :user_id'),
                    {"user_id": user_id}
                )
                row = result.fetchone()
                if row:
                    email = row[0]
                    logger.debug(f"Found email {email} for user {user_id}")
                    return email
                else:
                    logger.warning(f"No user found in database with id {user_id}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching user email for {user_id}: {e}", exc_info=True)
            return None


# Singleton instance
scheduler_service = SchedulerService()
