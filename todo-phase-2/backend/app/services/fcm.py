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
            logger.warning("FCM credentials not configured - FCM_CREDENTIALS_JSON is empty. "
                          "Native push notifications will not work.")
        else:
            self._initialize_firebase()

        # Log final status
        if self.enabled:
            logger.info("FCM Service initialized and ENABLED - native push notifications will work")
        else:
            logger.warning("FCM Service is DISABLED - native push notifications will NOT be sent")

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
        platform: str = "android",
    ) -> bool:
        """
        Send a push notification to a specific FCM token.
        Returns True if successful, False otherwise.

        For Android: Uses data-only messages for reliable background delivery.
        For Web: Uses notification+data for proper browser handling.
        """
        if not self.enabled:
            logger.debug("FCM disabled, skipping notification")
            return False

        try:
            # Prepare data payload with title and body included
            full_data = {
                "title": title,
                "body": body,
                "message": body,
                "channel_id": channel_id,
                **(data or {}),
            }
            # Ensure all values are strings (FCM requirement)
            full_data = {k: str(v) if v is not None else "" for k, v in full_data.items()}

            if platform == "android":
                # Data-only message for Android - ensures onMessageReceived is called
                message = messaging.Message(
                    data=full_data,
                    token=token,
                    android=messaging.AndroidConfig(
                        priority="high",
                        ttl=2419200,
                    ),
                )
            else:
                # Notification+data for web
                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
                    data=full_data,
                    token=token,
                )

            # Send the message
            response = messaging.send(message)
            logger.info(f"FCM notification sent successfully to {platform}: {response}")
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

        For Android: Uses data-only messages so our custom MessagingService
        always receives them (even when app is killed) and can show notifications.

        For Web: Uses notification+data for proper browser push display.
        """
        if not self.enabled:
            logger.debug("FCM is disabled, skipping push notification")
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
        # Include title and message in data for Android data-only messages
        data = {
            "notification_id": str(notification.id) if notification.id else "",
            "task_id": str(notification.task_id) if notification.task_id else "",
            "type": str(notification.type) if notification.type else "",
            "click_action": "OPEN_TASK" if notification.task_id else "OPEN_APP",
            "title": notification.title or "DoneKaro",
            "message": notification.message or "",
            "body": notification.message or "",
            "channel_id": channel_id,
        }

        success_count = 0
        invalid_tokens = []

        for fcm_token in tokens:
            try:
                if fcm_token.platform == "android":
                    # For Android: Use DATA-ONLY message
                    # This ensures onMessageReceived() is ALWAYS called,
                    # even when app is in background or killed.
                    # Our custom DoneKaroMessagingService will show the notification.
                    message = messaging.Message(
                        data=data,
                        token=fcm_token.token,
                        android=messaging.AndroidConfig(
                            priority="high",
                            ttl=2419200,
                        ),
                    )
                else:
                    # For Web: Use notification+data for proper browser push
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
                        webpush=webpush_config,
                    )

                response = messaging.send(message)
                logger.info(f"FCM sent to {fcm_token.platform} device: {response}")
                success_count += 1
            except messaging.UnregisteredError:
                logger.warning(f"Invalid FCM token, marking for removal: {fcm_token.id}")
                invalid_tokens.append(fcm_token)
            except messaging.SenderIdMismatchError:
                logger.error(f"FCM sender ID mismatch for token {fcm_token.id} - check Firebase project config")
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
