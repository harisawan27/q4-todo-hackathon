"""Email service for sending notifications"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import date, time

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications"""

    def __init__(self):
        self.settings = get_settings()

    def _get_smtp_connection(self) -> smtplib.SMTP:
        """Create and return an SMTP connection"""
        server = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port)
        server.starttls()
        if self.settings.smtp_user and self.settings.smtp_password:
            server.login(self.settings.smtp_user, self.settings.smtp_password)
        return server

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email to a recipient.
        Returns True if successful, False otherwise.
        """
        if not self.settings.email_enabled:
            logger.info(f"Email disabled. Would send to {to_email}: {subject}")
            return False

        if not self.settings.smtp_user or not self.settings.smtp_password:
            logger.warning("SMTP credentials not configured")
            return False

        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.settings.smtp_from_name} <{self.settings.smtp_from_email}>"
            msg["To"] = to_email

            # Add plain text version
            if plain_content:
                part1 = MIMEText(plain_content, "plain")
                msg.attach(part1)

            # Add HTML version
            part2 = MIMEText(html_content, "html")
            msg.attach(part2)

            # Send the email
            with self._get_smtp_connection() as server:
                server.sendmail(
                    self.settings.smtp_from_email,
                    to_email,
                    msg.as_string()
                )

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    def send_deadline_reminder(
        self,
        to_email: str,
        user_name: str,
        task_title: str,
        due_date: date,
        task_id: str,
    ) -> bool:
        """Send a deadline reminder email for a task"""
        subject = f"Reminder: Task '{task_title}' is due soon"

        due_date_str = due_date.strftime("%B %d, %Y")

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .task-box {{ background-color: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin: 15px 0; }}
                .task-title {{ font-size: 18px; font-weight: bold; color: #1f2937; }}
                .due-date {{ color: #dc2626; font-weight: bold; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                .btn {{ display: inline-block; background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; margin-top: 15px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Task Reminder</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name or 'there'},</p>
                    <p>This is a friendly reminder that you have an upcoming task deadline:</p>
                    <div class="task-box">
                        <div class="task-title">{task_title}</div>
                        <p>Due Date: <span class="due-date">{due_date_str}</span></p>
                    </div>
                    <p>Don't forget to complete this task before the deadline!</p>
                    <a href="https://q4-todo-hackathon.vercel.app/dashboard" class="btn">View Task</a>
                </div>
                <div class="footer">
                    <p>This email was sent by TaskFlow</p>
                    <p>You're receiving this because you have email notifications enabled.</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Task Reminder

        Hi {user_name or 'there'},

        This is a friendly reminder that you have an upcoming task deadline:

        Task: {task_title}
        Due Date: {due_date_str}

        Don't forget to complete this task before the deadline!

        View your tasks at: https://q4-todo-hackathon.vercel.app/dashboard

        ---
        This email was sent by TaskFlow
        """

        return self.send_email(to_email, subject, html_content, plain_content)

    def send_task_created_notification(
        self,
        to_email: str,
        user_name: str,
        task_title: str,
    ) -> bool:
        """Send notification when a task is created"""
        subject = f"New Task Created: {task_title}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #10b981; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .task-box {{ background-color: white; border: 1px solid #e5e7eb; border-radius: 8px; padding: 15px; margin: 15px 0; }}
                .task-title {{ font-size: 18px; font-weight: bold; color: #1f2937; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Task Created</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name or 'there'},</p>
                    <p>A new task has been added to your list:</p>
                    <div class="task-box">
                        <div class="task-title">{task_title}</div>
                    </div>
                </div>
                <div class="footer">
                    <p>This email was sent by TaskFlow</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Task Created

        Hi {user_name or 'there'},

        A new task has been added to your list:

        Task: {task_title}

        ---
        This email was sent by TaskFlow
        """

        return self.send_email(to_email, subject, html_content, plain_content)

    def send_task_completed_notification(
        self,
        to_email: str,
        user_name: str,
        task_title: str,
    ) -> bool:
        """Send notification when a task is completed"""
        subject = f"Task Completed: {task_title}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
                .content {{ background-color: #f9fafb; padding: 20px; border: 1px solid #e5e7eb; }}
                .success-icon {{ font-size: 48px; text-align: center; }}
                .task-title {{ font-size: 18px; font-weight: bold; color: #10b981; text-align: center; }}
                .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Task Completed!</h1>
                </div>
                <div class="content">
                    <p>Hi {user_name or 'there'},</p>
                    <p>Great job! You've completed a task:</p>
                    <p class="success-icon">&#10003;</p>
                    <p class="task-title">{task_title}</p>
                    <p style="text-align: center;">Keep up the great work!</p>
                </div>
                <div class="footer">
                    <p>This email was sent by TaskFlow</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        Task Completed!

        Hi {user_name or 'there'},

        Great job! You've completed a task:

        Task: {task_title}

        Keep up the great work!

        ---
        This email was sent by TaskFlow
        """

        return self.send_email(to_email, subject, html_content, plain_content)

    def send_deadline_reminder_urgent(
        self,
        to_email: str,
        user_name: Optional[str],
        task_title: str,
        due_date: date,
        due_time: Optional[time],
        task_id: str,
        urgency: str,  # "medium", "high", "critical"
        hours_remaining: float,
        reminder_level: "ReminderLevel",
    ) -> bool:
        """
        Send a Duolingo-style deadline reminder email with urgency-based styling.

        Urgency levels:
        - medium: 24h, 10h before (blue/calm)
        - high: 6h, 3h before (orange/warning)
        - critical: 1h before, overdue (red/urgent)
        """
        from app.models.notification import ReminderLevel

        # Urgency-based colors and messaging
        urgency_config = {
            "medium": {
                "header_bg": "#3B82F6",  # Blue
                "header_text": "Reminder",
                "accent_color": "#3B82F6",
                "emoji": "📅",
            },
            "high": {
                "header_bg": "#F59E0B",  # Orange
                "header_text": "Time is Running Out!",
                "accent_color": "#F59E0B",
                "emoji": "⚠️",
            },
            "critical": {
                "header_bg": "#EF4444",  # Red
                "header_text": "URGENT ACTION NEEDED",
                "accent_color": "#EF4444",
                "emoji": "🚨",
            },
        }

        config = urgency_config.get(urgency, urgency_config["medium"])

        # Format due date and time
        due_date_str = due_date.strftime("%B %d, %Y")
        if due_time:
            h = due_time.hour
            m = due_time.minute
            period = "PM" if h >= 12 else "AM"
            hour12 = h % 12 or 12
            due_time_str = f" at {hour12}:{m:02d} {period}"
        else:
            due_time_str = ""

        # Time remaining message
        if hours_remaining <= 0:
            time_msg = "This task is now <strong>OVERDUE</strong>!"
            time_badge = "OVERDUE"
            badge_color = "#EF4444"
        elif hours_remaining < 1:
            mins = int(hours_remaining * 60)
            time_msg = f"Only <strong>{mins} minutes</strong> remaining!"
            time_badge = f"{mins}m LEFT"
            badge_color = "#EF4444"
        elif hours_remaining < 24:
            hrs = int(hours_remaining)
            time_msg = f"Only <strong>{hrs} hour{'s' if hrs > 1 else ''}</strong> remaining!"
            time_badge = f"{hrs}h LEFT"
            badge_color = config["accent_color"]
        else:
            time_msg = "Due <strong>tomorrow</strong>!"
            time_badge = "DUE TOMORROW"
            badge_color = config["accent_color"]

        # Subject line based on urgency
        if urgency == "critical":
            subject = f"🚨 URGENT: '{task_title}' - {time_badge}"
        elif urgency == "high":
            subject = f"⚠️ '{task_title}' is due soon - {time_badge}"
        else:
            subject = f"📅 Reminder: '{task_title}' - {time_badge}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; margin: 0; padding: 0; background-color: #f3f4f6; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
                .header {{ background-color: {config['header_bg']}; color: white; padding: 30px 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; font-weight: 700; }}
                .header .emoji {{ font-size: 48px; display: block; margin-bottom: 10px; }}
                .content {{ padding: 30px 20px; }}
                .task-card {{ background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 2px solid {config['accent_color']}; border-radius: 12px; padding: 20px; margin: 20px 0; }}
                .task-title {{ font-size: 20px; font-weight: 700; color: #1f2937; margin-bottom: 10px; }}
                .task-meta {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; }}
                .badge {{ display: inline-block; background-color: {badge_color}; color: white; padding: 6px 12px; border-radius: 20px; font-size: 12px; font-weight: 700; letter-spacing: 0.5px; }}
                .due-info {{ color: #6b7280; font-size: 14px; }}
                .time-warning {{ background-color: #fef2f2; border-left: 4px solid {config['accent_color']}; padding: 15px; margin: 20px 0; border-radius: 0 8px 8px 0; }}
                .time-warning p {{ margin: 0; color: #991b1b; font-size: 16px; }}
                .cta-button {{ display: inline-block; background-color: {config['accent_color']}; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: 600; font-size: 16px; margin-top: 20px; }}
                .cta-button:hover {{ opacity: 0.9; }}
                .footer {{ text-align: center; padding: 20px; background-color: #f9fafb; color: #6b7280; font-size: 12px; border-top: 1px solid #e5e7eb; }}
                .motivation {{ font-style: italic; color: #6b7280; margin-top: 20px; padding: 15px; background-color: #f9fafb; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <span class="emoji">{config['emoji']}</span>
                    <h1>{config['header_text']}</h1>
                </div>
                <div class="content">
                    <p>Hi{(' ' + user_name) if user_name else ''},</p>

                    <div class="time-warning">
                        <p>{time_msg}</p>
                    </div>

                    <div class="task-card">
                        <div class="task-title">{task_title}</div>
                        <div class="task-meta">
                            <span class="badge">{time_badge}</span>
                            <span class="due-info">Due: {due_date_str}{due_time_str}</span>
                        </div>
                    </div>

                    <p>Don't let this task slip! Take action now to stay on track.</p>

                    <center>
                        <a href="https://q4-todo-hackathon.vercel.app/dashboard" class="cta-button">
                            Complete Task Now →
                        </a>
                    </center>

                    <div class="motivation">
                        💪 You've got this! Every completed task is a step toward your goals.
                    </div>
                </div>
                <div class="footer">
                    <p>This reminder was sent by <strong>TaskFlow</strong></p>
                    <p>We'll keep reminding you until this task is done - just like Duolingo! 🦉</p>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
        {config['header_text']}

        Hi{(' ' + user_name) if user_name else ''},

        {time_msg.replace('<strong>', '').replace('</strong>', '')}

        Task: {task_title}
        Due: {due_date_str}{due_time_str}
        Status: {time_badge}

        Don't let this task slip! Take action now to stay on track.

        Complete your task at: https://q4-todo-hackathon.vercel.app/dashboard

        You've got this! Every completed task is a step toward your goals.

        ---
        This reminder was sent by TaskFlow
        We'll keep reminding you until this task is done - just like Duolingo!
        """

        return self.send_email(to_email, subject, html_content, plain_content)


# Singleton instance
email_service = EmailService()
