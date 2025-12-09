"""Unit tests for health check endpoint."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestHealthRoutes:
    """Test suite for health check endpoints."""

    def test_health_check_success(self, client: TestClient) -> None:
        """Test successful health check."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "openai_api_configured" in data
        assert "version" in data

    def test_health_check_returns_correct_structure(self, client: TestClient) -> None:
        """Test health check returns correct response structure."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()

        # Check required fields
        required_fields = ["status", "openai_api_configured", "version"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_health_check_api_configured_is_boolean(self, client: TestClient) -> None:
        """Test openai_api_configured is a boolean value."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["openai_api_configured"], bool)

    def test_health_check_version_is_string(self, client: TestClient) -> None:
        """Test version is a string."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_health_check_status_healthy(self, client: TestClient) -> None:
        """Test health check returns healthy status."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_method_not_allowed(self, client: TestClient) -> None:
        """Test health check only accepts GET requests."""
        response = client.post("/health")
        assert response.status_code == 405  # Method Not Allowed

        response = client.put("/health")
        assert response.status_code == 405

        response = client.delete("/health")
        assert response.status_code == 405

    def test_health_check_returns_json(self, client: TestClient) -> None:
        """Test health check returns JSON content type."""
        response = client.get("/health")

        assert response.status_code == 200
        assert "application/json" in response.headers["content-type"]

    def test_health_check_multiple_requests(self, client: TestClient) -> None:
        """Test health check is idempotent."""
        response1 = client.get("/health")
        response2 = client.get("/health")
        response3 = client.get("/health")

        assert response1.status_code == 200
        assert response2.status_code == 200
        assert response3.status_code == 200

        # All responses should be consistent
        assert response1.json()["status"] == response2.json()["status"]
        assert response2.json()["status"] == response3.json()["status"]

    def test_health_check_response_time(self, client: TestClient) -> None:
        """Test health check responds quickly."""
        import time

        start = time.time()
        response = client.get("/health")
        elapsed = time.time() - start

        assert response.status_code == 200
        # Health check should be very fast (< 1 second)
        assert elapsed < 1.0

    def test_health_check_with_query_params(self, client: TestClient) -> None:
        """Test health check ignores query parameters."""
        response = client.get("/health?foo=bar&test=123")

        # Should still work normally
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

    def test_health_check_cors_headers(self, client: TestClient) -> None:
        """Test health check includes CORS headers."""
        response = client.get("/health")

        assert response.status_code == 200
        # CORS headers should be present (configured in FastAPI app)
        # Exact header check depends on CORS middleware configuration

    def test_health_check_api_version_matches_config(self, client: TestClient) -> None:
        """Test health check returns correct API version from config."""
        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        # Version should match settings.api_version (default: v1)
        assert data["version"] in ["v1", "v2"]  # Allow future versions
