"""Browser Web Push notification delivery service."""

import json
import logging
from typing import Optional

from pywebpush import WebPushException, webpush

from app import dapr_client
from app.services import state_service

logger = logging.getLogger("notification-service")

_vapid_claims: Optional[dict] = None
_vapid_private_key: Optional[str] = None


async def _load_vapid_keys() -> tuple[str, dict]:
    """Load VAPID keys from Dapr Secrets API."""
    global _vapid_private_key, _vapid_claims
    if _vapid_private_key is None:
        private_key_secret = await dapr_client.get_secret("vapid-private-key")
        _vapid_private_key = private_key_secret["vapid-private-key"]
        mailto_secret = await dapr_client.get_secret("vapid-mailto")
        _vapid_claims = {"sub": mailto_secret.get("vapid-mailto", "mailto:admin@donekaro.app")}
    return _vapid_private_key, _vapid_claims


async def send_notification(subscription_info: dict, title: str, body: str, url: str = "/") -> bool:
    """Send a push notification to a single subscription."""
    try:
        private_key, claims = await _load_vapid_keys()

        payload = json.dumps({
            "title": title,
            "body": body,
            "url": url,
            "icon": "/icon-192.png",
        })

        webpush(
            subscription_info=subscription_info,
            data=payload,
            vapid_private_key=private_key,
            vapid_claims=claims,
        )
        return True
    except WebPushException as e:
        if e.response and e.response.status_code == 410:
            logger.info(f"Push subscription gone (410): {subscription_info.get('endpoint', '')[:50]}")
            return False
        logger.error(f"Push notification failed: {e}")
        raise
    except Exception as e:
        logger.error(f"Push notification error: {e}")
        raise


async def send_to_user(user_id: str, title: str, body: str, url: str = "/") -> int:
    """Send push notification to all subscriptions for a user."""
    subscriptions = await state_service.get_push_subscriptions(user_id)
    sent_count = 0
    expired_ids = []

    for sub in subscriptions:
        sub_info = {
            "endpoint": sub.endpoint,
            "keys": {"auth": sub.auth, "p256dh": sub.p256dh},
        }
        try:
            success = await send_notification(sub_info, title, body, url)
            if success:
                sent_count += 1
            else:
                expired_ids.append(sub.id)
        except Exception:
            logger.warning(f"Failed to send to subscription {sub.id}")

    for sid in expired_ids:
        try:
            await state_service.delete_push_subscription(sid, user_id)
        except Exception as e:
            logger.warning(f"Failed to clean up expired subscription {sid}: {e}")

    logger.info(f"Sent {sent_count}/{len(subscriptions)} notifications to user {user_id}")
    return sent_count
