"""Shared test fixtures for notification-service tests."""

import sys
import os
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

# Ensure app package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def mock_dapr_client():
    """Mock individual functions on the app.dapr_client module."""
    import app.dapr_client as dc

    originals = {}
    funcs = ["get_state", "save_state", "bulk_get_state",
             "transact_state", "publish_event", "get_secret"]

    defaults = {
        "get_state": AsyncMock(return_value=(None, None)),
        "save_state": AsyncMock(),
        "bulk_get_state": AsyncMock(return_value=[]),
        "transact_state": AsyncMock(),
        "publish_event": AsyncMock(),
        "get_secret": AsyncMock(return_value={
            "private-key": "test-vapid-key",
            "mailto": "mailto:test@example.com",
        }),
    }

    for fn in funcs:
        originals[fn] = getattr(dc, fn)
        setattr(dc, fn, defaults[fn])

    yield dc

    # Restore originals
    for fn in funcs:
        setattr(dc, fn, originals[fn])


@pytest.fixture
def client(mock_dapr_client):
    """Create a FastAPI TestClient with mocked Dapr."""
    from app.main import app
    return TestClient(app)
