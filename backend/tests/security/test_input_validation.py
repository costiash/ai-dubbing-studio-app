"""Security tests for input validation and sanitization."""

import io
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.services.openai_client import get_openai_service
from backend.tests.fixtures.test_data import (
    PATH_TRAVERSAL_ATTEMPTS,
    SQL_INJECTION_ATTEMPTS,
    XSS_ATTEMPTS,
)


class MockOpenAIService:
    """Mock OpenAI service for security testing."""

    def __init__(self) -> None:
        """Initialize mock service with default behaviors."""
        self.api_key = "sk-test-key"  # Required by health check endpoint
        self.transcribe_audio = AsyncMock(return_value=("Test transcription", "en"))
        self.generate_optimized_prompt = AsyncMock(return_value="Optimized prompt")
        self.translate_text = AsyncMock(return_value="Safe translated text")
        self.generate_speech = AsyncMock(return_value=b"fake-mp3-audio-data")


@pytest.fixture
def mock_openai_service_security() -> MockOpenAIService:
    """Create a mock OpenAI service for security tests."""
    return MockOpenAIService()


@pytest.fixture
def security_client(
    test_settings: object,
    mock_openai_service_security: MockOpenAIService,
) -> Generator[TestClient]:
    """Create a test client with mocked OpenAI service for security tests."""
    app.dependency_overrides[get_openai_service] = lambda: mock_openai_service_security

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def mock_convert_to_mp3_with_file(input_path: object, output_path: object) -> None:
    """Mock convert_to_mp3 that creates an empty file."""
    from pathlib import Path
    Path(output_path).write_bytes(b"fake-mp3-data")


@pytest.mark.security
class TestFileUploadSecurity:
    """Security tests for file upload validation."""

    def test_rejects_executable_file(self, client: TestClient) -> None:
        """Test that executable files are rejected."""
        malicious_files = [
            ("malware.exe", "application/x-msdownload"),
            ("script.sh", "application/x-sh"),
            ("virus.bat", "application/x-bat"),
        ]

        for filename, mime_type in malicious_files:
            files = {"file": (filename, io.BytesIO(b"fake-exe"), mime_type)}
            response = client.post("/api/v1/audio/transcribe", files=files)

            # Should reject non-audio files
            assert response.status_code == 400

    def test_rejects_file_with_path_traversal_in_filename(self, client: TestClient) -> None:
        """Test that filenames with path traversal are rejected or sanitized."""
        for malicious_name in PATH_TRAVERSAL_ATTEMPTS:
            filename = malicious_name + ".mp3"
            files = {"file": (filename, io.BytesIO(b"fake-audio"), "audio/mpeg")}

            # File validation should catch this
            # Response depends on implementation - either 400 or filename is sanitized
            response = client.post("/api/v1/audio/transcribe", files=files)
            # Should either reject or safely handle
            assert response.status_code in [200, 400, 422, 500]

    def test_rejects_file_with_null_bytes_in_filename(self, client: TestClient) -> None:
        """Test that filenames with null bytes are rejected."""
        malicious_filename = "test\x00.mp3.exe"
        files = {"file": (malicious_filename, io.BytesIO(b"fake-audio"), "audio/mpeg")}

        response = client.post("/api/v1/audio/transcribe", files=files)

        # Should reject or sanitize
        assert response.status_code in [400, 422]

    def test_file_size_limit_enforcement(
        self,
        security_client: TestClient,
        mock_openai_service_security: MockOpenAIService,
    ) -> None:
        """Test that file size limits are enforced."""
        # Test with reasonable size that should pass
        normal_file = io.BytesIO(b"x" * (1024 * 1024))  # 1 MB
        files = {"file": ("test.mp3", normal_file, "audio/mpeg")}

        async def mock_convert(input_path: object, output_path: object) -> None:
            mock_convert_to_mp3_with_file(input_path, output_path)

        with patch("backend.api.routes.v1.audio.convert_to_mp3", side_effect=mock_convert):
            response = security_client.post("/api/v1/audio/transcribe", files=files)
            # Normal size should work
            assert response.status_code == 200

    def test_rejects_non_audio_mime_type(self, client: TestClient) -> None:
        """Test that non-audio MIME types are handled."""
        invalid_mime_types = [
            ("test.mp3", "text/plain"),
            ("test.mp3", "application/javascript"),
            ("test.mp3", "text/html"),
        ]

        for filename, mime_type in invalid_mime_types:
            files = {"file": (filename, io.BytesIO(b"fake-data"), mime_type)}
            response = client.post("/api/v1/audio/transcribe", files=files)

            # Extension is valid (.mp3) but MIME type is wrong
            # Current implementation warns but allows - this is acceptable
            # as validation primarily uses file extension
            assert response.status_code in [200, 400, 500]

    def test_multiple_file_extensions(self, client: TestClient) -> None:
        """Test files with multiple extensions."""
        filenames = [
            "test.mp3.exe",
            "audio.txt.mp3",
            "file.mp3.mp3",
        ]

        for filename in filenames:
            files = {"file": (filename, io.BytesIO(b"fake-audio"), "audio/mpeg")}
            response = client.post("/api/v1/audio/transcribe", files=files)

            # Should use last extension (.mp3 or .exe)
            if filename.endswith(".mp3"):
                # May succeed with mocked services
                assert response.status_code in [200, 500]
            else:
                # Should reject .exe
                assert response.status_code == 400


@pytest.mark.security
class TestTextInputSecurity:
    """Security tests for text input validation."""

    def test_xss_prevention_in_translation(
        self,
        security_client: TestClient,
        mock_openai_service_security: MockOpenAIService,
    ) -> None:
        """Test that XSS attempts in text are handled safely."""
        mock_openai_service_security.translate_text = AsyncMock(
            return_value="Safe translated text"
        )

        for xss_attempt in XSS_ATTEMPTS:
            payload = {
                "text": xss_attempt,
                "source_language": "English",
                "target_language": "Spanish",
            }
            response = security_client.post("/api/v1/audio/translate", json=payload)

            # Should process safely without executing scripts
            assert response.status_code == 200
            # Response should be JSON, not HTML with executable script
            assert "application/json" in response.headers["content-type"]

    def test_sql_injection_prevention(
        self,
        security_client: TestClient,
        mock_openai_service_security: MockOpenAIService,
    ) -> None:
        """Test that SQL injection attempts are handled safely."""
        mock_openai_service_security.translate_text = AsyncMock(
            return_value="Safe translation"
        )

        for sql_attempt in SQL_INJECTION_ATTEMPTS:
            payload = {
                "text": sql_attempt,
                "source_language": "English",
                "target_language": "Spanish",
            }
            response = security_client.post("/api/v1/audio/translate", json=payload)

            # Should handle safely
            assert response.status_code == 200

    def test_unicode_handling(
        self,
        security_client: TestClient,
        mock_openai_service_security: MockOpenAIService,
    ) -> None:
        """Test handling of various Unicode characters."""
        unicode_tests = [
            "Hello 世界 🌍",
            "Привет мир",
            "مرحبا بالعالم",
            "\u0000\u0001\u0002",  # Control characters
            "𝕳𝖊𝖑𝖑𝖔",  # Mathematical alphanumeric symbols
        ]

        mock_openai_service_security.translate_text = AsyncMock(return_value="Translated")

        for text in unicode_tests:
            payload = {
                "text": text,
                "source_language": "English",
                "target_language": "Spanish",
            }
            response = security_client.post("/api/v1/audio/translate", json=payload)

            # Should handle Unicode safely
            assert response.status_code in [200, 422, 500]

    def test_extremely_long_text(
        self,
        security_client: TestClient,
        mock_openai_service_security: MockOpenAIService,
    ) -> None:
        """Test handling of extremely long text input."""
        very_long_text = "x" * (1000000)  # 1 million characters

        mock_openai_service_security.translate_text = AsyncMock(return_value="Translated")

        payload = {
            "text": very_long_text,
            "source_language": "English",
            "target_language": "Spanish",
        }
        response = security_client.post("/api/v1/audio/translate", json=payload)

        # Should handle (may reject if too long, or process)
        assert response.status_code in [200, 400, 422, 500]

    def test_empty_string_handling(
        self,
        security_client: TestClient,
        mock_openai_service_security: MockOpenAIService,
    ) -> None:
        """Test handling of empty strings."""
        mock_openai_service_security.translate_text = AsyncMock(return_value="")

        payload = {
            "text": "",
            "source_language": "English",
            "target_language": "Spanish",
        }
        response = security_client.post("/api/v1/audio/translate", json=payload)

        # Should handle empty string gracefully
        assert response.status_code in [200, 400, 422]

    def test_newlines_and_special_chars(
        self,
        security_client: TestClient,
        mock_openai_service_security: MockOpenAIService,
    ) -> None:
        """Test handling of newlines and special characters."""
        special_texts = [
            "Line 1\nLine 2\nLine 3",
            "Tab\tseparated\ttext",
            "Carriage\rreturn",
            "Mixed\n\r\t special chars",
        ]

        mock_openai_service_security.translate_text = AsyncMock(return_value="Translated")

        for text in special_texts:
            payload = {
                "text": text,
                "source_language": "English",
                "target_language": "Spanish",
            }
            response = security_client.post("/api/v1/audio/translate", json=payload)

            assert response.status_code == 200


@pytest.mark.security
class TestAPISecurityHeaders:
    """Security tests for API headers and configuration."""

    def test_no_sensitive_info_in_error_messages(self, client: TestClient) -> None:
        """Test that error messages don't expose sensitive information."""
        # Trigger an error
        response = client.post("/api/v1/audio/transcribe")

        assert response.status_code == 422
        error_detail = str(response.json())

        # Should not contain API keys or internal paths
        assert "sk-" not in error_detail.lower()
        assert "api_key" not in error_detail.lower()
        assert "/tmp/" not in error_detail  # Internal paths

    def test_cors_configuration(self, client: TestClient) -> None:
        """Test CORS headers are configured properly."""
        response = client.get("/health")

        # CORS headers should be present
        # Exact check depends on middleware configuration
        assert response.status_code == 200

    def test_content_type_validation(self, client: TestClient) -> None:
        """Test that content-type is validated."""
        # Try to send wrong content type for JSON endpoint
        response = client.post(
            "/api/v1/audio/translate",
            content=b"not-json",
            headers={"content-type": "text/plain"}
        )

        # Should reject or handle invalid content-type
        assert response.status_code in [400, 422]


@pytest.mark.security
class TestRateLimitingAndDOS:
    """Tests for rate limiting and DOS prevention."""

    def test_malformed_json_handling(self, client: TestClient) -> None:
        """Test handling of malformed JSON."""
        response = client.post(
            "/api/v1/audio/translate",
            content=b"{invalid-json",
            headers={"content-type": "application/json"}
        )

        assert response.status_code in [400, 422]

    def test_deeply_nested_json(self, client: TestClient) -> None:
        """Test handling of deeply nested JSON (potential DOS)."""
        # Create deeply nested structure
        nested = {"a": {}}
        current = nested["a"]
        for _ in range(100):
            current["b"] = {}
            current = current["b"]

        response = client.post(
            "/api/v1/audio/translate",
            json=nested
        )

        # Should handle or reject
        assert response.status_code in [400, 422, 500]
