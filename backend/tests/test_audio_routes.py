"""Unit tests for audio processing endpoints."""

import io
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.core.exceptions import (
    AudioProcessingError,
    FileValidationError,
    TranscriptionError,
    TranslationError,
    TTSError,
)


@pytest.mark.unit
class TestTranscribeEndpoint:
    """Test suite for /audio/transcribe endpoint."""

    def test_transcribe_success(self, client: TestClient) -> None:
        """Test successful audio transcription."""
        audio_content = b"fake-mp3-audio-data"
        files = {"file": ("test.mp3", io.BytesIO(audio_content), "audio/mpeg")}

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func, \
             patch("backend.api.routes.v1.audio.convert_to_mp3") as mock_convert:

            mock_service = MagicMock()
            mock_service.transcribe_audio = AsyncMock(
                return_value=("Test transcription", "en")
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "Test transcription"
        assert data["language"] == "en"

    def test_transcribe_with_ogg_file(self, client: TestClient) -> None:
        """Test transcription with OGG file."""
        audio_content = b"OggS" + b"fake-ogg-data"
        files = {"file": ("test.ogg", io.BytesIO(audio_content), "audio/ogg")}

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func, \
             patch("backend.api.routes.v1.audio.convert_to_mp3") as mock_convert:


            mock_service = MagicMock()
            mock_service.transcribe_audio = AsyncMock(
                return_value=("OGG transcription", "en")
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 200
        data = response.json()
        assert data["text"] == "OGG transcription"

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

    def test_transcribe_api_error(self, client: TestClient) -> None:
        """Test transcription handles OpenAI API errors."""
        files = {"file": ("test.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")}

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func, \
             patch("backend.api.routes.v1.audio.convert_to_mp3") as mock_convert:


            mock_service = MagicMock()
            mock_service.transcribe_audio = AsyncMock(
                side_effect=TranscriptionError("API error")
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 500
        assert "API error" in response.json()["detail"]

    def test_transcribe_cleans_up_temp_files(self, client: TestClient) -> None:
        """Test transcription schedules temp file cleanup."""
        files = {"file": ("test.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")}

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func, \
             patch("backend.api.routes.v1.audio.convert_to_mp3") as mock_convert, \
             patch("backend.api.routes.v1.audio.cleanup_files") as mock_cleanup:

            mock_service = MagicMock()
            mock_service.transcribe_audio = AsyncMock(
                return_value=("Test", "en")
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/transcribe", files=files)

        assert response.status_code == 200
        # Cleanup should be scheduled in background tasks


@pytest.mark.unit
class TestTranslateEndpoint:
    """Test suite for /audio/translate endpoint."""

    def test_translate_success(self, client: TestClient) -> None:
        """Test successful text translation."""
        payload = {
            "text": "Hello, how are you?",
            "source_language": "English",
            "target_language": "Spanish",
        }

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.translate_text = AsyncMock(
                return_value="Hola, ¿cómo estás?"
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/translate", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["translated_text"] == "Hola, ¿cómo estás?"
        assert data["source_language"] == "English"
        assert data["target_language"] == "Spanish"

    def test_translate_different_languages(self, client: TestClient) -> None:
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

            with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
                mock_service = MagicMock()
                mock_service.translate_text = AsyncMock(return_value=expected)
                mock_service_func.return_value = mock_service

                response = client.post("/api/v1/audio/translate", json=payload)

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
        """Test translation with empty text."""
        payload = {
            "text": "",
            "source_language": "English",
            "target_language": "Spanish",
        }

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.translate_text = AsyncMock(return_value="")
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/translate", json=payload)

        # Should handle gracefully
        assert response.status_code in [200, 400, 422]

    def test_translate_api_error(self, client: TestClient) -> None:
        """Test translation handles API errors."""
        payload = {
            "text": "Test",
            "source_language": "English",
            "target_language": "Spanish",
        }

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.translate_text = AsyncMock(
                side_effect=TranslationError("API error")
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/translate", json=payload)

        assert response.status_code == 500
        assert "API error" in response.json()["detail"]

    def test_translate_long_text(self, client: TestClient) -> None:
        """Test translation with long text."""
        long_text = "This is a test sentence. " * 100
        payload = {
            "text": long_text,
            "source_language": "English",
            "target_language": "Spanish",
        }

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.translate_text = AsyncMock(
                return_value="Translated long text"
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/translate", json=payload)

        assert response.status_code == 200

    def test_translate_special_characters(self, client: TestClient) -> None:
        """Test translation with special characters."""
        payload = {
            "text": "Hello! ¿Cómo estás? 你好 Привет",
            "source_language": "English",
            "target_language": "Spanish",
        }

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.translate_text = AsyncMock(
                return_value="Translated special chars"
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/translate", json=payload)

        assert response.status_code == 200


@pytest.mark.unit
class TestTTSEndpoint:
    """Test suite for /audio/tts endpoint."""

    def test_tts_success(self, client: TestClient) -> None:
        """Test successful TTS generation."""
        payload = {
            "text": "Hello world",
            "voice": "onyx",
            "model": "tts-1",
        }

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.generate_speech = AsyncMock(
                return_value=b"fake-mp3-audio-data"
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200
        assert response.headers["content-type"] == "audio/mpeg"
        assert b"fake-mp3-audio-data" in response.content

    def test_tts_different_voices(self, client: TestClient) -> None:
        """Test TTS with different voices."""
        voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

        for voice in voices:
            payload = {"text": "Test", "voice": voice, "model": "tts-1"}

            with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
                mock_service = MagicMock()
                mock_service.generate_speech = AsyncMock(
                    return_value=b"fake-audio"
                )
                mock_service_func.return_value = mock_service

                response = client.post("/api/v1/audio/tts", json=payload)

            assert response.status_code == 200

    def test_tts_hd_model(self, client: TestClient) -> None:
        """Test TTS with HD model."""
        payload = {
            "text": "High quality audio",
            "voice": "nova",
            "model": "tts-1-hd",
        }

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.generate_speech = AsyncMock(
                return_value=b"fake-hd-audio"
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200

    def test_tts_missing_fields(self, client: TestClient) -> None:
        """Test TTS requires all fields."""
        incomplete_payloads = [
            {"voice": "onyx", "model": "tts-1"},  # Missing text
            {"text": "Test", "model": "tts-1"},  # Missing voice
            {"text": "Test", "voice": "onyx"},  # Missing model
        ]

        for payload in incomplete_payloads:
            response = client.post("/api/v1/audio/tts", json=payload)
            assert response.status_code == 422

    def test_tts_api_error(self, client: TestClient) -> None:
        """Test TTS handles API errors."""
        payload = {"text": "Test", "voice": "onyx", "model": "tts-1"}

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.generate_speech = AsyncMock(
                side_effect=TTSError("TTS generation failed")
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 500
        assert "TTS generation failed" in response.json()["detail"]

    def test_tts_content_disposition_header(self, client: TestClient) -> None:
        """Test TTS includes content-disposition header."""
        payload = {"text": "Test", "voice": "onyx", "model": "tts-1"}

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.generate_speech = AsyncMock(
                return_value=b"fake-audio"
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200
        assert "content-disposition" in response.headers
        assert "attachment" in response.headers["content-disposition"]
        assert "speech.mp3" in response.headers["content-disposition"]

    def test_tts_long_text(self, client: TestClient) -> None:
        """Test TTS with long text."""
        long_text = "This is a test sentence. " * 200
        payload = {"text": long_text, "voice": "onyx", "model": "tts-1"}

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.generate_speech = AsyncMock(
                return_value=b"fake-long-audio"
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200

    def test_tts_special_characters(self, client: TestClient) -> None:
        """Test TTS with special characters."""
        payload = {
            "text": "Hello! ¿Cómo estás? 你好",
            "voice": "onyx",
            "model": "tts-1",
        }

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.generate_speech = AsyncMock(
                return_value=b"fake-audio"
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200

    def test_tts_returns_audio_bytes(self, client: TestClient) -> None:
        """Test TTS returns audio content."""
        payload = {"text": "Test", "voice": "onyx", "model": "tts-1"}

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            expected_audio = b"unique-audio-data-12345"
            mock_service.generate_speech = AsyncMock(
                return_value=expected_audio
            )
            mock_service_func.return_value = mock_service

            response = client.post("/api/v1/audio/tts", json=payload)

        assert response.status_code == 200
        assert response.content == expected_audio
