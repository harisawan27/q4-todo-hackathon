"""Shared test fixtures for recurring-engine tests."""

import sys
import os
from unittest.mock import AsyncMock, MagicMock

import pytest

# Ensure app package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def mock_dapr_client(monkeypatch):
    """Mock the dapr_client module used by services."""
    mock = MagicMock()
    mock.register_job = AsyncMock()
    mock.delete_job = AsyncMock()
    mock.get_job = AsyncMock(return_value=None)
    mock.get_state = AsyncMock(return_value=(None, None))
    mock.save_state = AsyncMock()
    mock.publish_event = AsyncMock()
    monkeypatch.setattr("app.dapr_client", mock)
    return mock
