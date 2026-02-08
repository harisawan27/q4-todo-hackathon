"""Dapr State Management wrapper for chat-api task operations."""

import logging
from typing import Optional

import httpx

from app import dapr_client
from app.models.task import Task, TaskIndex

logger = logging.getLogger("chat-api")

# Max retries for transient state store failures
_MAX_RETRIES = 2


class StateStoreError(Exception):
    """Raised when the state store is unreachable after retries."""

    def __init__(self, message: str = "Task storage is temporarily unavailable. Please try again in a moment."):
        self.user_message = message
        super().__init__(message)


async def _retry_on_failure(operation, operation_name: str, retries: int = _MAX_RETRIES):
    """Execute an async operation with retry logic for transient failures."""
    last_error = None
    for attempt in range(retries + 1):
        try:
            return await operation()
        except (httpx.ConnectError, httpx.TimeoutException, httpx.RemoteProtocolError) as e:
            last_error = e
            logger.warning(
                f"State store {operation_name} failed (attempt {attempt + 1}/{retries + 1}): {e}"
            )
            if attempt < retries:
                import asyncio
                await asyncio.sleep(0.5 * (attempt + 1))
        except httpx.HTTPStatusError as e:
            if e.response.status_code >= 500:
                last_error = e
                logger.warning(
                    f"State store {operation_name} returned {e.response.status_code} "
                    f"(attempt {attempt + 1}/{retries + 1})"
                )
                if attempt < retries:
                    import asyncio
                    await asyncio.sleep(0.5 * (attempt + 1))
            else:
                raise
    logger.error(f"State store {operation_name} failed after {retries + 1} attempts: {last_error}")
    raise StateStoreError()


async def save_task(task: Task) -> None:
    """Save a task and update the user's task index atomically."""
    task_key = f"task--{task.id}"
    index_key = f"task-index--{task.user_id}"

    async def _do_save():
        index_data, index_etag = await dapr_client.get_state(index_key)
        if index_data:
            task_index = TaskIndex(**index_data)
        else:
            task_index = TaskIndex(user_id=task.user_id)

        if task.id not in task_index.task_ids:
            task_index.task_ids.append(task.id)

        operations = [
            {
                "operation": "upsert",
                "request": {"key": task_key, "value": task.model_dump(mode="json")},
            },
            {
                "operation": "upsert",
                "request": {"key": index_key, "value": task_index.model_dump(mode="json")},
            },
        ]
        await dapr_client.transact_state(operations)

    await _retry_on_failure(_do_save, "save_task")


async def get_task(task_id: str) -> Optional[tuple[Task, str | None]]:
    """Get a task by ID. Returns (Task, etag) or None."""

    async def _do_get():
        data, etag = await dapr_client.get_state(f"task--{task_id}")
        if data is None:
            return None
        return Task(**data), etag

    return await _retry_on_failure(_do_get, "get_task")


async def list_user_tasks(user_id: str) -> list[Task]:
    """List all tasks for a user using index-key pattern."""

    async def _do_list():
        index_data, _ = await dapr_client.get_state(f"task-index--{user_id}")
        if not index_data:
            return []

        task_index = TaskIndex(**index_data)
        if not task_index.task_ids:
            return []

        keys = [f"task--{tid}" for tid in task_index.task_ids]
        bulk_results = await dapr_client.bulk_get_state(keys)

        tasks = []
        for item in bulk_results:
            if item.get("data"):
                try:
                    task = Task(**item["data"])
                    if task.status != "deleted":
                        tasks.append(task)
                except Exception as e:
                    logger.warning(f"Failed to parse task: {e}")
        return sorted(tasks, key=lambda t: t.created_at, reverse=True)

    return await _retry_on_failure(_do_list, "list_user_tasks")


async def update_task(task: Task, etag: str | None = None) -> None:
    """Update a task with optional ETag concurrency control."""

    async def _do_update():
        item: dict = {"key": f"task--{task.id}", "value": task.model_dump(mode="json")}
        if etag:
            item["etag"] = etag
            item["options"] = {"concurrency": "first-write"}
        await dapr_client.save_state([item])

    await _retry_on_failure(_do_update, "update_task")


async def delete_task(task_id: str, user_id: str, etag: str | None = None) -> None:
    """Delete a task and remove from user index."""

    async def _do_delete():
        index_data, _ = await dapr_client.get_state(f"task-index--{user_id}")
        if index_data:
            task_index = TaskIndex(**index_data)
            task_index.task_ids = [tid for tid in task_index.task_ids if tid != task_id]
            operations = [
                {"operation": "delete", "request": {"key": f"task--{task_id}"}},
                {
                    "operation": "upsert",
                    "request": {
                        "key": f"task-index--{user_id}",
                        "value": task_index.model_dump(mode="json"),
                    },
                },
            ]
            await dapr_client.transact_state(operations)
        else:
            await dapr_client.delete_state(f"task--{task_id}", etag)

    await _retry_on_failure(_do_delete, "delete_task")
