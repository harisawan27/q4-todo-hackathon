"""Push notification subscription routes"""

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlmodel import Session, select

from app.auth.jwt_bearer import CurrentUser, get_current_user
from app.config import get_settings
from app.database import get_session
from app.models.push_subscription import (
    PushSubscription,
    PushSubscriptionCreate,
    PushSubscriptionRead,
)

router = APIRouter(prefix="/api/push", tags=["push"])
settings = get_settings()


@router.get("/vapid-key")
async def get_vapid_public_key() -> dict:
    """
    Get the VAPID public key for push subscription.
    This endpoint is public (no auth required) so the browser can subscribe.
    """
    if not settings.vapid_public_key:
        raise HTTPException(
            status_code=503,
            detail="Push notifications not configured"
        )

    return {
        "vapid_public_key": settings.vapid_public_key,
        "push_enabled": settings.push_enabled,
    }


@router.post("/subscribe", response_model=PushSubscriptionRead)
async def subscribe_to_push(
    subscription_data: PushSubscriptionCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
    user_agent: str | None = Header(default=None),
) -> PushSubscription:
    """
    Subscribe to push notifications.
    Creates or updates a subscription for the current user.
    """
    # Check if this subscription endpoint already exists for user
    existing = session.exec(
        select(PushSubscription).where(
            PushSubscription.user_id == current_user.user_id,
            PushSubscription.endpoint == subscription_data.endpoint,
        )
    ).first()

    if existing:
        # Update existing subscription keys
        existing.p256dh = subscription_data.keys.get("p256dh", "")
        existing.auth = subscription_data.keys.get("auth", "")
        existing.user_agent = user_agent
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing

    # Create new subscription
    subscription = PushSubscription(
        user_id=current_user.user_id,
        endpoint=subscription_data.endpoint,
        p256dh=subscription_data.keys.get("p256dh", ""),
        auth=subscription_data.keys.get("auth", ""),
        user_agent=user_agent,
    )

    session.add(subscription)
    session.commit()
    session.refresh(subscription)

    return subscription


@router.delete("/unsubscribe")
async def unsubscribe_from_push(
    endpoint: str,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> dict:
    """
    Unsubscribe from push notifications.
    Removes the subscription for the given endpoint.
    """
    subscription = session.exec(
        select(PushSubscription).where(
            PushSubscription.user_id == current_user.user_id,
            PushSubscription.endpoint == endpoint,
        )
    ).first()

    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")

    session.delete(subscription)
    session.commit()

    return {"success": True, "message": "Unsubscribed successfully"}


@router.get("/subscriptions", response_model=list[PushSubscriptionRead])
async def list_subscriptions(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> list[PushSubscription]:
    """
    List all push subscriptions for the current user.
    """
    subscriptions = session.exec(
        select(PushSubscription).where(
            PushSubscription.user_id == current_user.user_id
        )
    ).all()

    return list(subscriptions)
