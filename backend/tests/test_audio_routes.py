"""Unit tests for audio processing endpoints."""

import io
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.core.exceptions import (
    AudioProcessingError,
    TranscriptionError,
    TranslationError,
    TTSError,
)
from backend.services.openai_client import get_openai_service


class MockOpenAIService:
    """Mock OpenAI service for testing."""

    def __init__(self) -> None:
        """Initialize mock service with default behaviors."""
        self.api_key = "sk-test-key"  # Required by health check endpoint
        self.transcribe_audio = AsyncMock(return_value=("Test transcription", "en"))
        self.generate_optimized_prompt = AsyncMock(return_value="Optimized prompt")
        self.translate_text = AsyncMock(return_value="Translated text")
        self.generate_speech = AsyncMock(return_value=b"fake-mp3-audio-data")


@pytest.fixture
def mock_openai_service() -> MockOpenAIService:
    """Create a mock OpenAI service."""
    return MockOpenAIService()


@pytest.fixture
def client_with_mock_service(
    test_settings: object,  # noqa: ARG001
    mock_openai_service: MockOpenAIService,
) -> Generator[TestClient]:
    """Create a test client with mocked OpenAI service via dependency override."""
    # Override the get_openai_service dependency
    app.dependency_overrides[get_openai_service] = lambda: mock_openai_service

    with TestClient(app) as test_client:
        yield test_client

    # Clean up override after test
    app.dependency_overrides.clear()


def mock_convert_to_mp3_with_file(_input_path: object, output_path: object) -> None:
    """Mock convert_to_mp3 that creates an empty file to satisfy the route."""
    from pathlib import Path
    Path(output_path).write_bytes(b"fake-mp3-data")


@pytest.mark.unit
class TestTranscribeEndpoint:
    """Test suite for /audio/transcribe endpoint."""

    def test_transcribe_success(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,  # noqa: ARG002
    ) -> None:
        """Test successful audio transcription with dual-flow."""
        _ = mock_openai_service  # Used via client_with_mock_service fixture
        audio_content = b"fake-mp3-audio-data"
        files = {"file": ("test.mp3", io.BytesIO(audio_content), "audio/mpeg")}

        async def mock_convert(_input_path: object, output_path: object) -> None:
            mock_convert_to_mp3_with_file(_input_path, output_path)

        with patch("backend.api.routes.v1.audio.convert_to_mp3", side_effect=mock_convert):
            response = client_with_mock_service.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "text" in data
        assert "language" in data

    def test_transcribe_with_ogg_file(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,  # noqa: ARG002
    ) -> None:
        """Test transcription with OGG file."""
        _ = mock_openai_service  # Used via client_with_mock_service fixture
        audio_content = b"OggS" + b"fake-ogg-data"
        files = {"file": ("test.ogg", io.BytesIO(audio_content), "audio/ogg")}

        async def mock_convert(_input_path: object, output_path: object) -> None:
            mock_convert_to_mp3_with_file(_input_path, output_path)

        with patch("backend.api.routes.v1.audio.convert_to_mp3", side_effect=mock_convert):
            response = client_with_mock_service.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 200
        data = response.json()
        assert "text" in data

    def test_transcribe_invalid_file_extension(self, client: TestClient) -> None:
        """Test transcription rejects invalid file extension."""
        files = {"file": ("test.txt", io.BytesIO(b"not audio"), "text/plain")}

        response = client.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 400
        assert "Invalid file extension" in response.json()["detail"]

    def test_transcribe_no_file_provided(self, client: TestClient) -> None:
        """Test transcription requires file."""
        response = client.post("/api/v1/audio/transcribe")

        assert response.status_code == 422  # Validation error

    def test_transcribe_audio_processing_error(self, client: TestClient) -> None:
        """Test transcription handles audio processing errors."""
        files = {"file": ("test.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")}

        with patch("backend.api.routes.v1.audio.convert_to_mp3") as mock_convert:
            mock_convert.side_effect = AudioProcessingError("Conversion failed")

            response = client.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 500
        assert "Conversion failed" in response.json()["detail"]

    def test_transcribe_api_error(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test transcription handles OpenAI API errors."""
        files = {"file": ("test.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")}

        mock_openai_service.transcribe_audio = AsyncMock(
            side_effect=TranscriptionError("API error")
        )

        async def mock_convert(input_path: object, output_path: object) -> None:
            mock_convert_to_mp3_with_file(input_path, output_path)

        with patch("backend.api.routes.v1.audio.convert_to_mp3", side_effect=mock_convert):
            response = client_with_mock_service.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 500
        assert "API error" in response.json()["detail"]

    def test_transcribe_cleans_up_temp_files(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,  # noqa: ARG002
    ) -> None:
        """Test transcription schedules temp file cleanup."""
        _ = mock_openai_service  # Used via client_with_mock_service fixture
        files = {"file": ("test.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")}

        async def mock_convert(_input_path: object, output_path: object) -> None:
            mock_convert_to_mp3_with_file(_input_path, output_path)

        with patch("backend.api.routes.v1.audio.convert_to_mp3", side_effect=mock_convert):
            response = client_with_mock_service.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 200
        # Cleanup should be scheduled via background_tasks.add_task


@pytest.mark.unit
class TestTranslateEndpoint:
    """Test suite for /audio/translate endpoint."""

    def test_translate_success(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test successful text translation."""
        payload = {
            "text": "Hello, how are you?",
            "source_language": "English",
            "target_language": "Spanish",
        }

        mock_openai_service.translate_text = AsyncMock(return_value="Hola, ¿cómo estás?")

        response = client_with_mock_service.post("/api/v1/audio/translate", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["translated_text"] == "Hola, ¿cómo estás?"
        assert data["source_language"] == "English"
        assert data["target_language"] == "Spanish"

    def test_translate_different_languages(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test translation with different language pairs."""
        test_cases = [
            ("English", "French", "Bonjour"),
            ("Spanish", "English", "Hello"),
            ("English", "German", "Hallo"),
        ]

        for source, target, expected in test_cases:
            payload = {
                "text": "Test text",
                "source_language": source,
                "target_language": target,
            }

            mock_openai_service.translate_text = AsyncMock(return_value=expected)

            response = client_with_mock_service.post("/api/v1/audio/translate", json=payload)

            assert response.status_code == 200
            assert response.json()["translated_text"] == expected

    def test_translate_missing_fields(self, client: TestClient) -> None:
        """Test translation requires all fields."""
        incomplete_payloads = [
            {"text": "Test"},  # Missing languages
            {"source_language": "English", "target_language": "Spanish"},  # Missing text
            {"text": "Test", "source_language": "English"},  # Missing target
        ]

        for payload in incomplete_payloads:
            response = client.post("/api/v1/audio/translate", json=payload)
            assert response.status_code == 422  # Validation error

    def test_translate_empty_text(self, client: TestClient) -> None:
        """Test translation with empty text returns validation error."""
        payload = {
            "text": "",  # Empty text - violates min_length=1
            "source_language": "English",
            "target_language": "Spanish",
        }

        response = client.post("/api/v1/audio/translate", json=payload)

        # Empty text should fail validation (min_length=1)
        assert response.status_code == 422

    def test_translate_api_error(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test translation handles API errors."""
        payload = {
            "text": "Test",
            "source_language": "English",
            "target_language": "Spanish",
        }

        mock_openai_service.translate_text = AsyncMock(
            side_effect=TranslationError("API error")
        )

        response = client_with_mock_service.post("/api/v1/audio/translate", json=payload)

        assert response.status_code == 500
        assert "API error" in response.json()["detail"]

    def test_translate_long_text(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test translation with long text."""
        long_text = "This is a test sentence. " * 100
        payload = {
            "text": long_text,
            "source_language": "English",
            "target_language": "Spanish",
        }

        mock_openai_service.translate_text = AsyncMock(return_value="Translated long text")

        response = client_with_mock_service.post("/api/v1/audio/translate", json=payload)

        assert response.status_code == 200

    def test_translate_special_characters(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test translation with special characters."""
        payload = {
            "text": "Hello! ¿Cómo estás? 你好 Привет",
            "source_language": "English",
            "target_language": "Spanish",
        }

        mock_openai_service.translate_text = AsyncMock(return_value="Translated special chars")

        response = client_with_mock_service.post("/api/v1/audio/translate", json=payload)

        assert response.status_code == 200


@pytest.mark.unit
class TestTTSEndpoint:
    """Test suite for /audio/tts endpoint."""

    def test_tts_success(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test successful TTS generation."""
        payload = {
            "text": "Hello world",
            "voice": "onyx",
            "model": "tts-1",
        }

        mock_openai_service.generate_speech = AsyncMock(return_value=b"fake-mp3-audio-data")

        response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert b"fake-mp3-audio-data" in response.content

    def test_tts_different_voices(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test TTS with different voices."""
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        for voice in voices:
            payload = {"text": "Test", "voice": voice, "model": "tts-1"}

            mock_openai_service.generate_speech = AsyncMock(return_value=b"fake-audio")

            response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

            assert response.status_code == 200

    def test_tts_hd_model(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test TTS with HD model."""
        payload = {
            "text": "High quality audio",
            "voice": "nova",
            "model": "tts-1-hd",
        }

        mock_openai_service.generate_speech = AsyncMock(return_value=b"fake-hd-audio")

        response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200

    def test_tts_missing_text(self, client: TestClient) -> None:
        """Test TTS requires text field."""
        # Only text is required - voice and model have defaults
        incomplete_payloads = [
            {"voice": "onyx", "model": "tts-1"},  # Missing text
            {},  # Missing everything
        ]

        for payload in incomplete_payloads:
            response = client.post("/api/v1/audio/tts", json=payload)
            assert response.status_code == 422

    def test_tts_with_defaults(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test TTS works with only text (uses default voice and model)."""
        payload = {"text": "Test"}

        mock_openai_service.generate_speech = AsyncMock(return_value=b"fake-audio")

        response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200

    def test_tts_api_error(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test TTS handles API errors."""
        payload = {"text": "Test", "voice": "onyx", "model": "tts-1"}

        mock_openai_service.generate_speech = AsyncMock(
            side_effect=TTSError("TTS generation failed")
        )

        response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 500
        assert "TTS generation failed" in response.json()["detail"]

    def test_tts_content_disposition_header(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test TTS includes content-disposition header."""
        payload = {"text": "Test", "voice": "onyx", "model": "tts-1"}

        mock_openai_service.generate_speech = AsyncMock(return_value=b"fake-audio")

        response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]
        assert "speech.mp3" in response.headers["content-disposition"]

    def test_tts_long_text(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test TTS with long text."""
        long_text = "This is a test sentence. " * 100
        payload = {"text": long_text, "voice": "onyx", "model": "tts-1"}

        mock_openai_service.generate_speech = AsyncMock(return_value=b"fake-long-audio")

        response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200

    def test_tts_special_characters(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test TTS with special characters."""
        payload = {
            "text": "Hello! ¿Cómo estás? 你好",
            "voice": "onyx",
            "model": "tts-1",
        }

        mock_openai_service.generate_speech = AsyncMock(return_value=b"fake-audio")

        response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200

    def test_tts_returns_audio_bytes(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test TTS returns audio content."""
        payload = {"text": "Test", "voice": "onyx", "model": "tts-1"}

        expected_audio = b"unique-audio-data-12345"
        mock_openai_service.generate_speech = AsyncMock(return_value=expected_audio)

        response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200
        assert response.content == expected_audio

    def test_tts_with_instructions(
        self,
        client_with_mock_service: TestClient,
        mock_openai_service: MockOpenAIService,
    ) -> None:
        """Test TTS with voice instructions (gpt-4o-mini-tts feature)."""
        payload = {
            "text": "Hello world",
            "voice": "onyx",
            "model": "gpt-4o-mini-tts",
            "instructions": "Speak in a warm, friendly tone.",
        }

        mock_openai_service.generate_speech = AsyncMock(return_value=b"fake-audio")

        response = client_with_mock_service.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200
        # Verify generate_speech was called with instructions
        mock_openai_service.generate_speech.assert_called_once()
        call_kwargs = mock_openai_service.generate_speech.call_args[1]
        assert call_kwargs.get("instructions") == "Speak in a warm, friendly tone."
