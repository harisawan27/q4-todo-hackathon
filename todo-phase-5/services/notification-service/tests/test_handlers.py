"""Tests for notification event handlers."""

import json
from unittest.mock import AsyncMock, patch

import pytest


def test_health_endpoint(client):
    """Health endpoint should return 200."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "notification-service"


def test_reminder_fired_handler(client, mock_dapr_client):
    """Reminder-fired event should attempt push delivery."""
    mock_dapr_client.get_state = AsyncMock(return_value=(None, None))

    event = {
        "data": {
            "userId": "user-1",
            "taskId": "task-1",
            "data": {
                "taskTitle": "Buy groceries",
                "reminderLevel": "30-minutes-before",
            },
        },
    }

    with patch("app.handlers.reminder_handler.push_service") as mock_push:
        mock_push.send_to_user = AsyncMock(return_value=0)
        with patch("app.handlers.reminder_handler.state_service") as mock_state:
            mock_state.save_notification = AsyncMock()
            response = client.post("/events/reminder-fired", json=event)

    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"


def test_recurring_trigger_handler(client, mock_dapr_client):
    """Recurring-trigger event should attempt push delivery."""
    mock_dapr_client.get_state = AsyncMock(return_value=(None, None))

    event = {
        "data": {
            "userId": "user-1",
            "taskId": "task-1",
            "data": {
                "taskTitle": "Weekly Review",
            },
        },
    }

    with patch("app.handlers.reminder_handler.push_service") as mock_push:
        mock_push.send_to_user = AsyncMock(return_value=1)
        with patch("app.handlers.reminder_handler.state_service") as mock_state:
            mock_state.save_notification = AsyncMock()
            response = client.post("/events/recurring-trigger", json=event)

    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"


def test_task_updates_handler(client, mock_dapr_client):
    """Task-updates event should process successfully."""
    event = {
        "data": {
            "userId": "user-1",
            "data": {
                "action": "completed",
                "task": {"title": "My Task"},
            },
        },
    }

    with patch("app.handlers.task_update_handler.push_service") as mock_push:
        mock_push.send_to_user = AsyncMock(return_value=1)
        response = client.post("/events/task-updates", json=event)

    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"


def test_reminders_default_handler(client, mock_dapr_client):
    """Default reminders handler should return SUCCESS."""
    response = client.post("/events/reminders", json={})
    assert response.status_code == 200
    assert response.json()["status"] == "SUCCESS"
