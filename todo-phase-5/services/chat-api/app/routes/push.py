"""Push subscription management endpoints."""

import uuid

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.middleware.auth import get_current_user

router = APIRouter(prefix="/push", tags=["Push"])


class PushSubscriptionRequest(BaseModel):
    endpoint: str
    auth: str
    p256dh: str


class PushUnsubscribeRequest(BaseModel):
    endpoint: str


@router.post("/subscribe", status_code=status.HTTP_201_CREATED)
async def register_push_subscription(
    request: PushSubscriptionRequest,
    user_id: str = Depends(get_current_user),
):
    """Register a browser push subscription for the authenticated user."""
    from app import dapr_client

    sub_id = str(uuid.uuid4())

    sub_data = {
        "id": sub_id,
        "user_id": user_id,
        "endpoint": request.endpoint,
        "auth": request.auth,
        "p256dh": request.p256dh,
    }

    await dapr_client.save_state([{
        "key": f"push-subscription--{sub_id}",
        "value": sub_data,
    }])

    index_key = f"push-sub-index--{user_id}"
    index_data, _ = await dapr_client.get_state(index_key)
    if index_data:
        sub_ids = index_data.get("subscription_ids", [])
    else:
        sub_ids = []

    sub_ids.append(sub_id)
    await dapr_client.save_state([{
        "key": index_key,
        "value": {"user_id": user_id, "subscription_ids": sub_ids},
    }])

    return {"id": sub_id, "status": "registered"}


@router.post("/unsubscribe", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_push_subscription(
    request: PushUnsubscribeRequest,
    user_id: str = Depends(get_current_user),
):
    """Unregister a browser push subscription."""
    from app import dapr_client

    index_key = f"push-sub-index--{user_id}"
    index_data, _ = await dapr_client.get_state(index_key)
    if not index_data:
        return

    sub_ids = index_data.get("subscription_ids", [])
    for sid in sub_ids:
        sub_data, _ = await dapr_client.get_state(f"push-subscription--{sid}")
        if sub_data and sub_data.get("endpoint") == request.endpoint:
            await dapr_client.delete_state(f"push-subscription--{sid}")
            sub_ids.remove(sid)
            await dapr_client.save_state([{
                "key": index_key,
                "value": {"user_id": user_id, "subscription_ids": sub_ids},
            }])
            break
