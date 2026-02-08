"""Dapr State Management wrapper for notification-service."""

import logging
from typing import Optional

from app import dapr_client
from app.models.notification import Notification
from app.models.subscription import PushSubscription, PushSubscriptionIndex

logger = logging.getLogger("notification-service")


async def save_notification(notification: Notification) -> None:
    """Save a notification record."""
    await dapr_client.save_state([{
        "key": f"notification--{notification.id}",
        "value": notification.model_dump(mode="json"),
    }])


async def get_push_subscriptions(user_id: str) -> list[PushSubscription]:
    """Get all push subscriptions for a user."""
    index_data, _ = await dapr_client.get_state(f"push-sub-index--{user_id}")
    if not index_data:
        return []

    index = PushSubscriptionIndex(**index_data)
    if not index.subscription_ids:
        return []

    keys = [f"push-subscription--{sid}" for sid in index.subscription_ids]
    bulk_results = await dapr_client.bulk_get_state(keys)

    subscriptions = []
    for item in bulk_results:
        if item.get("data"):
            try:
                subscriptions.append(PushSubscription(**item["data"]))
            except Exception as e:
                logger.warning(f"Failed to parse push subscription: {e}")
    return subscriptions


async def save_push_subscription(subscription: PushSubscription) -> None:
    """Save a push subscription and update user index."""
    sub_key = f"push-subscription--{subscription.id}"
    index_key = f"push-sub-index--{subscription.user_id}"

    index_data, _ = await dapr_client.get_state(index_key)
    if index_data:
        index = PushSubscriptionIndex(**index_data)
    else:
        index = PushSubscriptionIndex(user_id=subscription.user_id)

    if subscription.id not in index.subscription_ids:
        index.subscription_ids.append(subscription.id)

    await dapr_client.transact_state([
        {"operation": "upsert", "request": {"key": sub_key, "value": subscription.model_dump(mode="json")}},
        {"operation": "upsert", "request": {"key": index_key, "value": index.model_dump(mode="json")}},
    ])


async def delete_push_subscription(subscription_id: str, user_id: str) -> None:
    """Delete a push subscription and update user index."""
    index_key = f"push-sub-index--{user_id}"
    index_data, _ = await dapr_client.get_state(index_key)

    operations = [
        {"operation": "delete", "request": {"key": f"push-subscription--{subscription_id}"}},
    ]

    if index_data:
        index = PushSubscriptionIndex(**index_data)
        index.subscription_ids = [sid for sid in index.subscription_ids if sid != subscription_id]
        operations.append({
            "operation": "upsert",
            "request": {"key": index_key, "value": index.model_dump(mode="json")},
        })

    await dapr_client.transact_state(operations)
