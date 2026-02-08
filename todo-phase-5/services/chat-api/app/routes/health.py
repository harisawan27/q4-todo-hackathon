"""Health check endpoint for Kubernetes liveness/readiness probes."""

import logging

import httpx
from fastapi import APIRouter

from app.config import settings

router = APIRouter(tags=["System"])
logger = logging.getLogger("chat-api")

DAPR_BASE_URL = f"http://localhost:{settings.dapr_http_port}"


@router.get("/health")
async def health_check():
    """Check service health including Dapr sidecar connectivity."""
    dapr_status = {"connected": False, "state_store": "unavailable", "pubsub": "unavailable"}

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            # Check Dapr sidecar health
            resp = await client.get(f"{DAPR_BASE_URL}/v1.0/healthz")
            if resp.status_code == 204 or resp.status_code == 200:
                dapr_status["connected"] = True

            # Check state store availability
            try:
                await client.get(f"{DAPR_BASE_URL}/v1.0/state/statestore-postgres/health-check-probe")
                dapr_status["state_store"] = "available"
            except Exception:
                pass

            # Check pubsub availability
            try:
                resp = await client.get(f"{DAPR_BASE_URL}/v1.0/metadata")
                if resp.status_code == 200:
                    dapr_status["pubsub"] = "available"
            except Exception:
                pass
    except Exception as e:
        logger.warning(f"Dapr health check failed: {e}")

    overall = "healthy" if dapr_status["connected"] else "degraded"
    return {
        "status": overall,
        "service": settings.service_name,
        "version": "1.0.0",
        "dapr": dapr_status,
    }
