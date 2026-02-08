"""Async Dapr HTTP client wrapper for notification-service."""

import os
from typing import Any

import httpx

DAPR_HTTP_PORT = int(os.environ.get("DAPR_HTTP_PORT", "3501"))
DAPR_BASE_URL = f"http://localhost:{DAPR_HTTP_PORT}"

STATE_STORE = "statestore-postgres"
PUBSUB_NAME = "pubsub-kafka"
SECRET_STORE = "local-secrets"


async def publish_event(topic: str, data: dict[str, Any], metadata: dict[str, str] | None = None) -> None:
    """Publish an event to a Kafka topic via Dapr Pub/Sub."""
    headers: dict[str, str] = {"Content-Type": "application/cloudevents+json"}
    if metadata:
        for k, v in metadata.items():
            headers[f"metadata.{k}"] = v
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DAPR_BASE_URL}/v1.0/publish/{PUBSUB_NAME}/{topic}",
            json=data,
            headers=headers,
        )
        resp.raise_for_status()


async def get_state(key: str) -> tuple[Any, str | None]:
    """Get state by key. Returns (data, etag) tuple."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}/{key}")
        if resp.status_code == 204 or not resp.content:
            return None, None
        etag = resp.headers.get("ETag")
        return resp.json(), etag


async def save_state(items: list[dict[str, Any]]) -> None:
    """Save one or more state items."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}",
            json=items,
        )
        resp.raise_for_status()


async def delete_state(key: str, etag: str | None = None) -> None:
    """Delete a state entry by key."""
    headers: dict[str, str] = {}
    if etag:
        headers["If-Match"] = etag
    async with httpx.AsyncClient() as client:
        resp = await client.delete(
            f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}/{key}",
            headers=headers,
        )
        resp.raise_for_status()


async def bulk_get_state(keys: list[str]) -> list[dict[str, Any]]:
    """Bulk get multiple state items by keys."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}/bulk",
            json={"keys": keys},
        )
        resp.raise_for_status()
        return resp.json()


async def transact_state(operations: list[dict[str, Any]]) -> None:
    """Execute a state transaction."""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{DAPR_BASE_URL}/v1.0/state/{STATE_STORE}/transaction",
            json={"operations": operations},
        )
        resp.raise_for_status()


async def get_secret(secret_name: str) -> dict[str, str]:
    """Get a secret from the Dapr secret store."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{DAPR_BASE_URL}/v1.0/secrets/{SECRET_STORE}/{secret_name}",
        )
        resp.raise_for_status()
        return resp.json()
