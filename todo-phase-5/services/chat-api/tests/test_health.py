"""Tests for the health check endpoint."""


def test_health_endpoint_returns_200(client):
    """Health endpoint should return 200 with service info."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["service"] == "chat-api"
    assert data["version"] == "1.0.0"
    assert "status" in data
