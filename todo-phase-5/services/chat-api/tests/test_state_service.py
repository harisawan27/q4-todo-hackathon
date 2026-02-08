"""Tests for state_service — task CRUD with mocked Dapr client."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import httpx
import pytest

from app.models.task import Task, TaskIndex
from app.services.state_service import (
    StateStoreError,
    delete_task,
    get_task,
    list_user_tasks,
    save_task,
    update_task,
)


@pytest.fixture
def sample_task():
    return Task(
        id="task-1",
        user_id="user-1",
        title="Test Task",
        created_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
        updated_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )


@pytest.mark.asyncio
async def test_save_task_new(mock_dapr_client, sample_task):
    """Saving a new task should transact state with task + index."""
    mock_dapr_client.get_state = AsyncMock(return_value=(None, None))
    await save_task(sample_task)
    mock_dapr_client.transact_state.assert_called_once()
    ops = mock_dapr_client.transact_state.call_args[0][0]
    assert len(ops) == 2
    assert ops[0]["operation"] == "upsert"
    assert ops[0]["request"]["key"] == "task--task-1"


@pytest.mark.asyncio
async def test_save_task_existing_index(mock_dapr_client, sample_task):
    """Saving when index already exists should append task_id."""
    existing_index = TaskIndex(user_id="user-1", task_ids=["task-0"])
    mock_dapr_client.get_state = AsyncMock(
        return_value=(existing_index.model_dump(mode="json"), "etag-1")
    )
    await save_task(sample_task)
    mock_dapr_client.transact_state.assert_called_once()
    ops = mock_dapr_client.transact_state.call_args[0][0]
    index_value = ops[1]["request"]["value"]
    assert "task-1" in index_value["task_ids"]
    assert "task-0" in index_value["task_ids"]


@pytest.mark.asyncio
async def test_get_task_found(mock_dapr_client, sample_task):
    """Getting an existing task should return (Task, etag)."""
    mock_dapr_client.get_state = AsyncMock(
        return_value=(sample_task.model_dump(mode="json"), "etag-1")
    )
    result = await get_task("task-1")
    assert result is not None
    task, etag = result
    assert task.id == "task-1"
    assert etag == "etag-1"


@pytest.mark.asyncio
async def test_get_task_not_found(mock_dapr_client):
    """Getting a non-existent task should return None."""
    mock_dapr_client.get_state = AsyncMock(return_value=(None, None))
    result = await get_task("nonexistent")
    assert result is None


@pytest.mark.asyncio
async def test_list_user_tasks_empty(mock_dapr_client):
    """Listing tasks for user with no index should return empty list."""
    mock_dapr_client.get_state = AsyncMock(return_value=(None, None))
    result = await list_user_tasks("user-1")
    assert result == []


@pytest.mark.asyncio
async def test_list_user_tasks_with_tasks(mock_dapr_client, sample_task):
    """Listing tasks should return tasks from bulk get."""
    index = TaskIndex(user_id="user-1", task_ids=["task-1"])
    mock_dapr_client.get_state = AsyncMock(
        return_value=(index.model_dump(mode="json"), None)
    )
    mock_dapr_client.bulk_get_state = AsyncMock(
        return_value=[{"data": sample_task.model_dump(mode="json")}]
    )
    result = await list_user_tasks("user-1")
    assert len(result) == 1
    assert result[0].id == "task-1"


@pytest.mark.asyncio
async def test_update_task(mock_dapr_client, sample_task):
    """Update should call save_state."""
    await update_task(sample_task)
    mock_dapr_client.save_state.assert_called_once()


@pytest.mark.asyncio
async def test_delete_task(mock_dapr_client):
    """Delete should transact: remove task key + update index."""
    index = TaskIndex(user_id="user-1", task_ids=["task-1", "task-2"])
    mock_dapr_client.get_state = AsyncMock(
        return_value=(index.model_dump(mode="json"), None)
    )
    await delete_task("task-1", "user-1")
    mock_dapr_client.transact_state.assert_called_once()
    ops = mock_dapr_client.transact_state.call_args[0][0]
    assert ops[0]["operation"] == "delete"
    index_value = ops[1]["request"]["value"]
    assert "task-1" not in index_value["task_ids"]
    assert "task-2" in index_value["task_ids"]


@pytest.mark.asyncio
async def test_retry_on_connect_error(mock_dapr_client):
    """Should retry on transient connect errors then succeed."""
    call_count = 0

    async def flaky_get(key):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise httpx.ConnectError("Connection refused")
        return None, None

    mock_dapr_client.get_state = flaky_get
    result = await get_task("task-1")
    assert result is None
    assert call_count == 2
