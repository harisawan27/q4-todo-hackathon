"""SSE endpoint for real-time task updates and Dapr event handler."""

import asyncio
import json
import logging

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

logger = logging.getLogger("chat-api")

router = APIRouter(tags=["Events"])

# In-memory map of user_id -> list of asyncio.Queue
sse_connections: dict[str, list[asyncio.Queue]] = {}


@router.get("/events/stream")
async def sse_stream(request: Request, userId: str):
    """Server-Sent Events endpoint for real-time task updates."""
    queue: asyncio.Queue = asyncio.Queue()
    sse_connections.setdefault(userId, []).append(queue)

    async def event_generator():
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    event = await asyncio.wait_for(queue.get(), timeout=30.0)
                    event_id = event.get("id", "")
                    event_data = json.dumps(event.get("data", {}))
                    yield f"id: {event_id}\nevent: task-update\ndata: {event_data}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            if userId in sse_connections:
                try:
                    sse_connections[userId].remove(queue)
                except ValueError:
                    pass
                if not sse_connections[userId]:
                    del sse_connections[userId]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/events/task-updates")
async def handle_task_updates(request: Request):
    """Dapr subscription handler — receives task-update broadcasts from Kafka."""
    event = await request.json()
    data = event.get("data", {})
    user_id = data.get("userId", "")
    event_data = data.get("data", {})

    if user_id and user_id in sse_connections:
        sse_event = {
            "id": data.get("eventId", ""),
            "data": event_data,
        }
        for queue in sse_connections[user_id]:
            try:
                await queue.put(sse_event)
            except Exception:
                pass

    return {"status": "SUCCESS"}
