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

        Reminder Schedule (Duolingo-style persistence):
        - 24 hours (1 day) before deadline - medium urgency
        - 12 hours before deadline - medium urgency
        - 6 hours before deadline - high urgency
        - 3 hours before deadline - high urgency
        - 1 hour before deadline - critical urgency
        - Overdue - critical urgency

        Reminders STOP when task is marked as completed.
        """
        from app.models.notification import ReminderLevel

        # Urgency-based colors and messaging (Duolingo-inspired)
        urgency_config = {
            "medium": {
                "header_bg": "#58CC02",  # Duolingo green
                "header_text": "Friendly Reminder",
                "accent_color": "#58CC02",
                "emoji": "🦉",
                "gradient": "linear-gradient(135deg, #58CC02 0%, #46a302 100%)",
            },
            "high": {
                "header_bg": "#FF9600",  # Duolingo orange
                "header_text": "Time is Running Out!",
                "accent_color": "#FF9600",
                "emoji": "⏰",
                "gradient": "linear-gradient(135deg, #FF9600 0%, #e68600 100%)",
            },
            "critical": {
                "header_bg": "#FF4B4B",  # Duolingo red
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

        # Time remaining message with Duolingo-style urgency
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

        # Subject line based on urgency (Duolingo-style)
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
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', sans-serif; line-height: 1.6; color: #3c3c3c; margin: 0; padding: 0; background-color: #f7f7f7; }}
                .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); }}
                .header {{ background: {config['gradient']}; color: white; padding: 40px 20px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 28px; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.2); }}
                .header .mascot {{ font-size: 64px; display: block; margin-bottom: 15px; filter: drop-shadow(0 4px 8px rgba(0,0,0,0.2)); }}
                .content {{ padding: 32px 24px; }}
                .greeting {{ font-size: 18px; color: #4b4b4b; margin-bottom: 20px; }}
                .task-card {{ background: linear-gradient(145deg, #ffffff 0%, #f8f8f8 100%); border: 3px solid {config['accent_color']}; border-radius: 16px; padding: 24px; margin: 24px 0; box-shadow: 0 4px 12px rgba(0,0,0,0.08); }}
                .task-title {{ font-size: 22px; font-weight: 700; color: #1a1a1a; margin-bottom: 12px; }}
                .task-meta {{ display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-top: 16px; }}
                .badge {{ display: inline-block; background: {badge_color}; color: white; padding: 8px 16px; border-radius: 25px; font-size: 13px; font-weight: 800; letter-spacing: 1px; text-transform: uppercase; box-shadow: 0 2px 8px rgba(0,0,0,0.15); }}
                .due-info {{ color: #777; font-size: 14px; font-weight: 500; }}
                .time-warning {{ background: linear-gradient(135deg, #fff8f0 0%, #fff0e0 100%); border-left: 5px solid {config['accent_color']}; padding: 20px; margin: 24px 0; border-radius: 0 12px 12px 0; }}
                .time-warning p {{ margin: 0; color: #333; font-size: 18px; font-weight: 600; }}
                .cta-section {{ text-align: center; margin: 32px 0; }}
                .cta-button {{ display: inline-block; background: {config['gradient']}; color: white; padding: 16px 40px; text-decoration: none; border-radius: 12px; font-weight: 700; font-size: 18px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); transition: transform 0.2s; }}
                .cta-button:hover {{ transform: translateY(-2px); }}
                .motivation-box {{ background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%); border-radius: 12px; padding: 20px; margin-top: 24px; text-align: center; }}
                .motivation-box p {{ margin: 0; color: #0369a1; font-size: 16px; font-weight: 500; }}
                .motivation-box .icon {{ font-size: 28px; margin-bottom: 8px; display: block; }}
                .footer {{ text-align: center; padding: 24px; background-color: #f9fafb; color: #6b7280; font-size: 13px; border-top: 1px solid #e5e7eb; }}
                .footer strong {{ color: #58CC02; }}
                .reminder-note {{ background: #fffbeb; border: 1px solid #fcd34d; border-radius: 8px; padding: 12px; margin-top: 16px; font-size: 12px; color: #92400e; }}
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
                        <p class="greeting">Hi{(' ' + user_name) if user_name else ' there'}!</p>

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

                        <div class="cta-section">
                            <a href="https://q4-todo-hackathon.vercel.app/dashboard" class="cta-button">
                                Complete Task Now
                            </a>
                        </div>

                        <div class="motivation-box">
                            <span class="icon">💪</span>
                            <p>{motivational_msg}</p>
                        </div>

                        <div class="reminder-note">
                            <strong>Note:</strong> We'll keep sending reminders until you mark this task as complete - just like Duolingo does! Complete it to stop the reminders.
                        </div>
                    </div>
                    <div class="footer">
                        <p>Sent with 💚 by <strong>DoneKaro</strong></p>
                        <p style="margin-top: 8px;">Your productivity companion that won't let you forget!</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        plain_content = f"""
{config['header_text'].upper()}

Hi{(' ' + user_name) if user_name else ' there'}!

{time_msg.replace('<strong>', '').replace('</strong>', '').replace("<strong style='color: #FF4B4B;'>", '').replace("<strong style='color: #FF9600;'>", '').replace("<strong style='color: #58CC02;'>", '')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TASK: {task_title}
DUE: {due_date_str}{due_time_str}
STATUS: {time_badge}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{motivational_msg}

Complete your task at: https://q4-todo-hackathon.vercel.app/dashboard

---

Note: We'll keep sending reminders until you mark this task as complete - just like Duolingo! Complete it to stop the reminders.

Sent with love by DoneKaro
Your productivity companion that won't let you forget!
        """

        return self.send_email(to_email, subject, html_content, plain_content)


# Singleton instance
email_service = EmailService()
