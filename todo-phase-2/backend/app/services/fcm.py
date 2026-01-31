"""Firebase Cloud Messaging (FCM) service for push notifications"""

import json
import logging
from typing import Optional

import firebase_admin
from firebase_admin import credentials, messaging
from sqlmodel import Session, select

from app.config import get_settings
from app.models.fcm_token import FCMToken
from app.models.notification import Notification

logger = logging.getLogger(__name__)
settings = get_settings()


class FCMService:
    """Service for sending FCM push notifications"""

    def __init__(self):
        self.enabled = settings.fcm_enabled and bool(settings.fcm_credentials_json)
        self._initialized = False

        if not settings.fcm_enabled:
            logger.info("FCM is disabled via FCM_ENABLED setting")
        elif not settings.fcm_credentials_json:
            logger.warning("FCM credentials not configured - FCM_CREDENTIALS_JSON is empty")
        else:
            self._initialize_firebase()

    def _initialize_firebase(self):
        """Initialize Firebase Admin SDK"""
        if self._initialized:
            return

        try:
            # Check if already initialized
            try:
                firebase_admin.get_app()
                self._initialized = True
                logger.info("Firebase Admin SDK already initialized")
                return
            except ValueError:
                pass

            # Parse credentials from JSON string
            creds_dict = json.loads(settings.fcm_credentials_json)
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
            self._initialized = True
            logger.info("Firebase Admin SDK initialized successfully")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid FCM credentials JSON: {e}")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {e}")
            self.enabled = False

    def send_notification(
        self,
        token: str,
        title: str,
        body: str,
        data: Optional[dict] = None,
        channel_id: str = "task-updates",
    ) -> bool:
        """
        Send a push notification to a specific FCM token.
        Returns True if successful, False otherwise.
        """
        if not self.enabled:
            logger.debug("FCM disabled, skipping notification")
            return False

        try:
            # Build the message
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                token=token,
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        channel_id=channel_id,
                        priority="high",
                        default_sound=True,
                        default_vibrate_timings=True,
                    ),
                ),
            )

            # Send the message
            response = messaging.send(message)
            logger.info(f"FCM notification sent successfully: {response}")
            return True
        except messaging.UnregisteredError:
            logger.warning(f"FCM token is unregistered/invalid: {token[:20]}...")
            return False
        except messaging.SenderIdMismatchError:
            logger.error("FCM sender ID mismatch - check Firebase project config")
            return False
        except Exception as e:
            logger.error(f"Failed to send FCM notification: {e}")
            return False

    def send_to_user(
        self,
        session: Session,
        user_id: str,
        notification: Notification,
    ) -> int:
        """
        Send push notification to all FCM tokens for a user.
        Returns the number of successful deliveries.
        """
        if not self.enabled:
            return 0

        # Get all FCM tokens for user
        statement = select(FCMToken).where(FCMToken.user_id == user_id)
        tokens = session.exec(statement).all()

        if not tokens:
            logger.debug(f"No FCM tokens found for user {user_id}")
            return 0

        # Determine channel based on notification type
        channel_id = "task-updates"
        if notification.type in ("deadline_approaching", "deadline_passed"):
            channel_id = "deadline-alerts"

        # Prepare data payload (FCM requires all values to be strings)
        data = {
            "notification_id": str(notification.id) if notification.id else "",
            "task_id": str(notification.task_id) if notification.task_id else "",
            "type": str(notification.type) if notification.type else "",
            "click_action": "OPEN_TASK" if notification.task_id else "OPEN_APP",
        }

        success_count = 0
        invalid_tokens = []

        for fcm_token in tokens:
            try:
                # Build platform-specific config based on token platform
                android_config = None
                webpush_config = None

                if fcm_token.platform == "android":
                    android_config = messaging.AndroidConfig(
                        priority="high",
                        notification=messaging.AndroidNotification(
                            channel_id=channel_id,
                            priority="high",
                            default_sound=True,
                            default_vibrate_timings=True,
                        ),
                    )
                elif fcm_token.platform == "web":
                    # Web push config for browsers
                    webpush_config = messaging.WebpushConfig(
                        notification=messaging.WebpushNotification(
                            title=notification.title,
                            body=notification.message,
                            icon="/android-chrome-192x192.png",
                            badge="/favicon-32x32.png",
                            tag=str(notification.id) if notification.id else None,
                            require_interaction=notification.type in ("deadline_approaching", "deadline_passed"),
                        ),
                        fcm_options=messaging.WebpushFCMOptions(
                            link="/dashboard/tasks" if notification.task_id else "/dashboard"
                        ),
                    )

                message = messaging.Message(
                    notification=messaging.Notification(
                        title=notification.title,
                        body=notification.message,
                    ),
                    data=data,
                    token=fcm_token.token,
                    android=android_config,
                    webpush=webpush_config,
                )

                response = messaging.send(message)
                logger.info(f"FCM sent to {fcm_token.platform}: {response}")
                success_count += 1
            except messaging.UnregisteredError:
                logger.warning(f"Invalid FCM token, marking for removal: {fcm_token.id}")
                invalid_tokens.append(fcm_token)
            except Exception as e:
                logger.error(f"FCM send failed for token {fcm_token.id}: {e}")

        # Clean up invalid tokens
        for invalid in invalid_tokens:
            session.delete(invalid)

        if invalid_tokens:
            session.commit()
            logger.info(f"Removed {len(invalid_tokens)} invalid FCM tokens")

        return success_count

    def send_multicast(
        self,
        tokens: list[str],
        title: str,
        body: str,
        data: Optional[dict] = None,
    ) -> tuple[int, int]:
        """
        Send notification to multiple tokens at once (batch).
        Returns (success_count, failure_count).
        """
        if not self.enabled or not tokens:
            return 0, 0

        try:
            message = messaging.MulticastMessage(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                ),
                data=data or {},
                tokens=tokens,
                android=messaging.AndroidConfig(
                    priority="high",
                    notification=messaging.AndroidNotification(
                        priority="high",
                        default_sound=True,
                    ),
                ),
            )

            response = messaging.send_each_for_multicast(message)
            logger.info(
                f"FCM multicast: {response.success_count} success, "
                f"{response.failure_count} failures"
            )
            return response.success_count, response.failure_count
        except Exception as e:
            logger.error(f"FCM multicast failed: {e}")
            return 0, len(tokens)


# Singleton instance
fcm_service = FCMService()
