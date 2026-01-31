"""FCM (Firebase Cloud Messaging) token management routes"""

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from app.auth.jwt_bearer import CurrentUser, get_current_user
from app.database import get_session
from app.models.fcm_token import FCMToken, FCMTokenCreate, FCMTokenResponse
from app.services.fcm import fcm_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/push/fcm", tags=["FCM Push Notifications"])


@router.post("/register", response_model=FCMTokenResponse)
async def register_fcm_token(
    token_data: FCMTokenCreate,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Register an FCM token for push notifications.
    If the token already exists for this user, updates the timestamp.
    If it exists for a different user, reassigns it to current user.
    """
    # Check if token already exists
    statement = select(FCMToken).where(FCMToken.token == token_data.token)
    existing = session.exec(statement).first()

    if existing:
        # Update existing token
        existing.user_id = current_user.user_id
        existing.platform = token_data.platform
        existing.device_info = token_data.device_info
        existing.updated_at = datetime.now(timezone.utc)
        session.add(existing)
        session.commit()
        session.refresh(existing)
        logger.info(f"Updated FCM token for user {current_user.user_id}")
        return existing

    # Create new token
    fcm_token = FCMToken(
        user_id=current_user.user_id,
        token=token_data.token,
        platform=token_data.platform,
        device_info=token_data.device_info,
    )
    session.add(fcm_token)
    session.commit()
    session.refresh(fcm_token)
    logger.info(f"Registered new FCM token for user {current_user.user_id}")
    return fcm_token


@router.delete("/unregister")
async def unregister_fcm_token(
    token: str = Query(..., description="FCM token to unregister"),
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Unregister an FCM token (e.g., on logout)"""
    statement = select(FCMToken).where(
        FCMToken.token == token,
        FCMToken.user_id == current_user.user_id,
    )
    fcm_token = session.exec(statement).first()

    if not fcm_token:
        raise HTTPException(status_code=404, detail="Token not found")

    session.delete(fcm_token)
    session.commit()
    logger.info(f"Unregistered FCM token for user {current_user.user_id}")
    return {"message": "Token unregistered successfully"}


@router.get("/tokens", response_model=list[FCMTokenResponse])
async def list_fcm_tokens(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """List all FCM tokens registered for the current user"""
    statement = select(FCMToken).where(FCMToken.user_id == current_user.user_id)
    tokens = session.exec(statement).all()
    return tokens


@router.delete("/tokens")
async def clear_all_tokens(
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """Clear all FCM tokens for current user (e.g., on account deletion)"""
    statement = select(FCMToken).where(FCMToken.user_id == current_user.user_id)
    tokens = session.exec(statement).all()

    count = len(tokens)
    for token in tokens:
        session.delete(token)

    session.commit()
    logger.info(f"Cleared {count} FCM tokens for user {current_user.user_id}")
    return {"message": f"Cleared {count} FCM token(s)"}


class TestNotificationRequest(BaseModel):
    title: str = "Test Notification"
    body: str = "This is a test push notification from DoneKaro!"


@router.post("/test")
async def test_fcm_notification(
    request: TestNotificationRequest,
    current_user: CurrentUser = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    """
    Send a test FCM notification to all registered devices for current user.
    Use this to verify FCM is working correctly.
    """
    # Check if FCM is enabled
    if not fcm_service.enabled:
        raise HTTPException(
            status_code=503,
            detail="FCM is not enabled. Check FCM_CREDENTIALS_JSON environment variable."
        )

    # Get all FCM tokens for user
    statement = select(FCMToken).where(FCMToken.user_id == current_user.user_id)
    tokens = session.exec(statement).all()

    if not tokens:
        raise HTTPException(
            status_code=404,
            detail="No FCM tokens registered. Open the app on your device first."
        )

    # Send test notification to each token
    success_count = 0
    failed_tokens = []

    for fcm_token in tokens:
        result = fcm_service.send_notification(
            token=fcm_token.token,
            title=request.title,
            body=request.body,
            data={
                "type": "test",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            channel_id="task-updates",
        )
        if result:
            success_count += 1
        else:
            failed_tokens.append(fcm_token.id)

    logger.info(f"Test notification: {success_count}/{len(tokens)} sent for user {current_user.user_id}")

    return {
        "message": f"Test notification sent to {success_count}/{len(tokens)} device(s)",
        "success_count": success_count,
        "total_tokens": len(tokens),
        "failed_token_ids": failed_tokens,
    }
