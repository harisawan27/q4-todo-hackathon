"""Email service using Resend API - Simple and free (100 emails/day)"""

import logging
from typing import Optional
from datetime import date, time

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)


class EmailService:
    """
    Email service using Resend API.

    Setup:
    1. Sign up at https://resend.com (free)
    2. Get your API key from the dashboard
    3. Set RESEND_API_KEY in your .env

    Free tier: 100 emails/day, 3000/month
    """

    RESEND_API_URL = "https://api.resend.com/emails"

    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.resend_api_key
        self.from_email = self.settings.email_from or "DoneKaro <onboarding@resend.dev>"
        self.enabled = self.settings.email_enabled and bool(self.api_key)

        if self.enabled:
            logger.info("Email service enabled (Resend)")
        else:
            logger.info("Email service disabled (no RESEND_API_KEY)")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> bool:
        """
        Send an email using Resend API.
        Returns True if successful, False otherwise.
        """
        if not self.enabled:
            logger.info(f"Email disabled. Would send to {to_email}: {subject}")
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.RESEND_API_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": self.from_email,
                        "to": [to_email],
                        "subject": subject,
                        "html": html_content,
                        "text": plain_content,
                    },
                    timeout=10.0,
                )

                if response.status_code == 200:
                    result = response.json()
                    logger.info(f"Email sent successfully to {to_email}, id: {result.get('id')}")
                    return True
                else:
                    logger.error(f"Resend API error {response.status_code}: {response.text}")
                    return False

        except httpx.TimeoutException:
            logger.error(f"Email request timed out for {to_email}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    # Synchronous wrapper for backwards compatibility with scheduler
    def send_email_sync(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        plain_content: Optional[str] = None,
    ) -> bool:
        """Synchronous version of send_email for use in scheduler"""
        import asyncio

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # We're in an async context, create a new task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.send_email(to_email, subject, html_content, plain_content)
                    )
                    return future.result(timeout=15)
            else:
                return loop.run_until_complete(
                    self.send_email(to_email, subject, html_content, plain_content)
                )
        except Exception as e:
            logger.error(f"Sync email send failed: {e}")
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
                    <p>This email was sent by DoneKaro</p>
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
        This email was sent by DoneKaro
        """

        return self.send_email_sync(to_email, subject, html_content, plain_content)

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
                    <p>This email was sent by DoneKaro</p>
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
        This email was sent by DoneKaro
        """

        return self.send_email_sync(to_email, subject, html_content, plain_content)

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
                    <p>This email was sent by DoneKaro</p>
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
        This email was sent by DoneKaro
        """

        return self.send_email_sync(to_email, subject, html_content, plain_content)

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
        """
        from app.models.notification import ReminderLevel

        # Urgency-based colors and messaging (Duolingo-inspired)
        urgency_config = {
            "medium": {
                "header_bg": "#58CC02",
                "header_text": "Friendly Reminder",
                "accent_color": "#58CC02",
                "emoji": "🦉",
                "gradient": "linear-gradient(135deg, #58CC02 0%, #46a302 100%)",
            },
            "high": {
                "header_bg": "#FF9600",
                "header_text": "Time is Running Out!",
                "accent_color": "#FF9600",
                "emoji": "⏰",
                "gradient": "linear-gradient(135deg, #FF9600 0%, #e68600 100%)",
            },
            "critical": {
                "header_bg": "#FF4B4B",
                "header_text": "Don't Break Your Streak!",
                "accent_color": "#FF4B4B",
                "emoji": "🔥",
                "gradient": "linear-gradient(135deg, #FF4B4B 0%, #e63939 100%)",
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
            time_msg = "This task is now <strong style='color: #FF4B4B;'>OVERDUE</strong>!"
            time_badge = "OVERDUE"
            badge_color = "#FF4B4B"
            motivational_msg = "It's not too late! Complete it now and get back on track."
        elif hours_remaining < 1:
            mins = int(hours_remaining * 60)
            time_msg = f"Only <strong style='color: #FF4B4B;'>{mins} minutes</strong> left!"
            time_badge = f"{mins}m LEFT"
            badge_color = "#FF4B4B"
            motivational_msg = "Final push! You're so close to finishing."
        elif hours_remaining <= 3:
            hrs = int(hours_remaining)
            time_msg = f"<strong style='color: #FF4B4B;'>{hrs} hour{'s' if hrs > 1 else ''}</strong> until deadline!"
            time_badge = f"{hrs}h LEFT"
            badge_color = "#FF4B4B"
            motivational_msg = "Crunch time! Focus and finish strong."
        elif hours_remaining <= 6:
            hrs = int(hours_remaining)
            time_msg = f"<strong style='color: #FF9600;'>{hrs} hours</strong> remaining!"
            time_badge = f"{hrs}h LEFT"
            badge_color = "#FF9600"
            motivational_msg = "You've got this! Start now and finish with time to spare."
        elif hours_remaining <= 12:
            hrs = int(hours_remaining)
            time_msg = f"<strong style='color: #58CC02;'>{hrs} hours</strong> until your deadline."
            time_badge = f"{hrs}h LEFT"
            badge_color = config["accent_color"]
            motivational_msg = "Perfect time to knock this out! Half a day to go."
        else:
            time_msg = "Due <strong style='color: #58CC02;'>tomorrow</strong>!"
            time_badge = "DUE TOMORROW"
            badge_color = config["accent_color"]
            motivational_msg = "Plan ahead today for a stress-free tomorrow!"

        # Subject line based on urgency
        if urgency == "critical":
            subject = f"🔥 '{task_title}' needs you NOW - {time_badge}"
        elif urgency == "high":
            subject = f"⏰ Time check: '{task_title}' - {time_badge}"
        else:
            subject = f"🦉 Hey! Don't forget '{task_title}' - {time_badge}"

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #3c3c3c; margin: 0; padding: 0; background-color: #f7f7f7; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .header {{ background: {config['gradient']}; color: white; padding: 40px 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; font-weight: 800; }}
                .header .mascot {{ font-size: 64px; display: block; margin-bottom: 15px; }}
                .content {{ padding: 32px 24px; }}
                .task-card {{ background: #f8f8f8; border: 3px solid {config['accent_color']}; border-radius: 16px; padding: 24px; margin: 24px 0; }}
                .task-title {{ font-size: 22px; font-weight: 700; color: #1a1a1a; margin-bottom: 12px; }}
                .badge {{ display: inline-block; background: {badge_color}; color: white; padding: 8px 16px; border-radius: 25px; font-size: 13px; font-weight: 800; }}
                .time-warning {{ background: #fff8f0; border-left: 5px solid {config['accent_color']}; padding: 20px; margin: 24px 0; border-radius: 0 12px 12px 0; }}
                .cta-button {{ display: inline-block; background: {config['gradient']}; color: white; padding: 16px 40px; text-decoration: none; border-radius: 12px; font-weight: 700; font-size: 18px; }}
                .motivation-box {{ background: #f0f9ff; border-radius: 12px; padding: 20px; margin-top: 24px; text-align: center; }}
                .footer {{ text-align: center; padding: 24px; background-color: #f9fafb; color: #6b7280; font-size: 13px; }}
            </style>
        </head>
        <body>
            <div style="padding: 20px; background-color: #f7f7f7;">
                <div class="container">
                    <div class="header">
                        <span class="mascot">{config['emoji']}</span>
                        <h1>{config['header_text']}</h1>
                    </div>
                    <div class="content">
                        <p>Hi{(' ' + user_name) if user_name else ' there'}!</p>
                        <div class="time-warning">
                            <p style="margin:0; font-size: 18px; font-weight: 600;">{time_msg}</p>
                        </div>
                        <div class="task-card">
                            <div class="task-title">{task_title}</div>
                            <span class="badge">{time_badge}</span>
                            <p style="color: #777; margin-top: 12px;">Due: {due_date_str}{due_time_str}</p>
                        </div>
                        <div style="text-align: center; margin: 32px 0;">
                            <a href="https://q4-todo-hackathon.vercel.app/dashboard" class="cta-button">Complete Task Now</a>
                        </div>
                        <div class="motivation-box">
                            <p style="font-size: 28px; margin-bottom: 8px;">💪</p>
                            <p style="margin: 0; color: #0369a1;">{motivational_msg}</p>
                        </div>
                    </div>
                    <div class="footer">
                        <p>Sent with 💚 by <strong style="color: #58CC02;">DoneKaro</strong></p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
{config['header_text'].upper()}

Hi{(' ' + user_name) if user_name else ' there'}!

TASK: {task_title}
DUE: {due_date_str}{due_time_str}
STATUS: {time_badge}

{motivational_msg}

Complete your task at: https://q4-todo-hackathon.vercel.app/dashboard

---
Sent by DoneKaro
        """

        return self.send_email_sync(to_email, subject, html_content, plain_content)


# Singleton instance
email_service = EmailService()
