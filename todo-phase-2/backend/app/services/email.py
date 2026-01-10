"""Email service for sending notifications"""

import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from datetime import date

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


# Singleton instance
email_service = EmailService()
