"""Web Push notification service using pywebpush"""

import json
import logging

from pywebpush import webpush, WebPushException
from sqlmodel import Session, select

from app.config import get_settings
from app.models.notification import Notification
from app.models.push_subscription import PushSubscription

logger = logging.getLogger(__name__)
settings = get_settings()


class WebPushService:
    """Service for sending Web Push notifications"""

    def __init__(self):
        self.vapid_private_key = settings.vapid_private_key
        self.vapid_claims = {"sub": f"mailto:{settings.vapid_email}"}
        self.enabled = settings.push_enabled and bool(settings.vapid_private_key)

    def send_notification(
        self,
        subscription: PushSubscription,
        title: str,
        message: str,
        notification_id: str | None = None,
        task_id: str | None = None,
        notification_type: str | None = None,
    ) -> bool:
        """
        Send a push notification to a specific subscription.
        Returns True if successful, False otherwise.
        """
        if not self.enabled:
            logger.debug("Web push disabled, skipping notification")
            return False

        subscription_info = {
            "endpoint": subscription.endpoint,
            "keys": {
                "p256dh": subscription.p256dh,
                "auth": subscription.auth,
            },
        }

        payload = json.dumps({
            "title": title,
            "message": message,
            "notification_id": notification_id,
            "task_id": task_id,
            "type": notification_type,
        })

        try:
            webpush(
                subscription_info=subscription_info,
                data=payload,
                vapid_private_key=self.vapid_private_key,
                vapid_claims=self.vapid_claims,
            )
            logger.info(f"Push notification sent to endpoint: {subscription.endpoint[:50]}...")
            return True
        except WebPushException as e:
            logger.error(f"Web push failed: {e}")
            if e.response and e.response.status_code in (404, 410):
                logger.info(f"Subscription expired, should be removed: {subscription.id}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending push: {e}")
            return False

    def send_to_user(
        self,
        session: Session,
        user_id: str,
        notification: Notification,
    ) -> int:
        """
        Send push notification to all subscriptions for a user.
        Returns the number of successful deliveries.
        """
        if not self.enabled:
            return 0

        # Get all subscriptions for user
        statement = select(PushSubscription).where(
            PushSubscription.user_id == user_id
        )
        subscriptions = session.exec(statement).all()

        if not subscriptions:
            logger.debug(f"No push subscriptions found for user {user_id}")
            return 0

        success_count = 0
        expired_subscriptions = []

        for subscription in subscriptions:
            try:
                subscription_info = {
                    "endpoint": subscription.endpoint,
                    "keys": {
                        "p256dh": subscription.p256dh,
                        "auth": subscription.auth,
                    },
                }

                payload = json.dumps({
                    "title": notification.title,
                    "message": notification.message,
                    "notification_id": notification.id,
                    "task_id": notification.task_id,
                    "type": notification.type,
                })

                webpush(
                    subscription_info=subscription_info,
                    data=payload,
                    vapid_private_key=self.vapid_private_key,
                    vapid_claims=self.vapid_claims,
                )
                success_count += 1
            except WebPushException as e:
                logger.error(f"Push failed for subscription {subscription.id}: {e}")
                if e.response and e.response.status_code in (404, 410):
                    expired_subscriptions.append(subscription)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")

        # Clean up expired subscriptions
        for expired in expired_subscriptions:
            session.delete(expired)

        if expired_subscriptions:
            session.commit()
            logger.info(f"Removed {len(expired_subscriptions)} expired subscriptions")

        return success_count


# Singleton instance
webpush_service = WebPushService()
