"""Tests for API endpoints"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for health check endpoint"""

    def test_health_check(self, client: TestClient):
        """Test health endpoint returns healthy status"""
        response = client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


class TestChatEndpoint:
    """Tests for chat endpoint"""

    def test_chat_empty_message(self, client: TestClient, user_id: str):
        """Test chat with empty message returns 400"""
        response = client.post(
            f"/api/{user_id}/chat",
            json={"message": ""}
        )

        assert response.status_code == 422  # Validation error

    def test_chat_whitespace_message(self, client: TestClient, user_id: str):
        """Test chat with whitespace-only message returns 400"""
        response = client.post(
            f"/api/{user_id}/chat",
            json={"message": "   "}
        )

        assert response.status_code == 400
