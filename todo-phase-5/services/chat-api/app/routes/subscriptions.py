"""Dapr programmatic subscription endpoint (fallback for non-K8s environments)."""

from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/dapr/subscribe")
async def get_dapr_subscriptions():
    """Return programmatic Dapr subscription list."""
    return [
        {
            "pubsubname": "pubsub-kafka",
            "topic": "task-updates",
            "route": "/events/task-updates",
        },
        {
            "pubsubname": "pubsub-kafka",
            "topic": "task-events",
            "route": "/events/audit-task-events",
        },
    ]
