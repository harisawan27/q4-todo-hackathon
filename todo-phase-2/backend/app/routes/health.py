"""Health check endpoint"""

from datetime import datetime, timezone

from fastapi import APIRouter

router = APIRouter(tags=["System"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint - no authentication required"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
