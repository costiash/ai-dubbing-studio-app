"""Integration tests for complete API workflows."""

import concurrent.futures
import io
from collections.abc import Generator
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.core.exceptions import TranscriptionError, TranslationError
from backend.services.openai_client import get_openai_service


class MockOpenAIService:
    """Mock OpenAI service for integration testing."""

    def __init__(self) -> None:
        """Initialize mock service with default behaviors."""
        self.api_key = "sk-test-key"  # Required by health check endpoint
        self.transcribe_audio = AsyncMock(return_value=("Test transcription", "en"))
        self.generate_optimized_prompt = AsyncMock(return_value="Optimized prompt")
        self.translate_text = AsyncMock(return_value="Translated text")
        self.generate_speech = AsyncMock(return_value=b"fake-mp3-audio-data")


@pytest.fixture
def mock_openai_service_integration() -> MockOpenAIService:
    """Create a mock OpenAI service for integration tests."""
    return MockOpenAIService()


@pytest.fixture
def integration_client(
    test_settings: object,
    mock_openai_service_integration: MockOpenAIService,
) -> Generator[TestClient]:
    """Create a test client with mocked OpenAI service for integration tests."""
    app.dependency_overrides[get_openai_service] = lambda: mock_openai_service_integration

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def mock_convert_to_mp3_with_file(input_path: object, output_path: object) -> None:
    """Mock convert_to_mp3 that creates an empty file."""
    from pathlib import Path
    Path(output_path).write_bytes(b"fake-mp3-data")


@pytest.mark.integration
class TestCompleteWorkflows:
    """Integration tests for end-to-end workflows."""

    def test_complete_dubbing_workflow(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test complete workflow: upload → transcribe → translate → TTS."""
        # Configure mocks
        mock_openai_service_integration.transcribe_audio = AsyncMock(
            return_value=("Hello world", "en")
        )
        mock_openai_service_integration.translate_text = AsyncMock(
            return_value="Hola mundo"
        )
        mock_openai_service_integration.generate_speech = AsyncMock(
            return_value=b"fake-spanish-audio"
        )

        async def mock_convert(input_path: object, output_path: object) -> None:
            mock_convert_to_mp3_with_file(input_path, output_path)

        with patch("backend.api.routes.v1.audio.convert_to_mp3", side_effect=mock_convert):
            # Step 1: Transcribe
            audio_file = ("test.mp3", io.BytesIO(b"fake-audio-data"), "audio/mpeg")
            transcribe_response = integration_client.post(
                "/api/v1/audio/transcribe",
                files={"file": audio_file}
            )
            assert transcribe_response.status_code == 200
            transcription = transcribe_response.json()
            assert transcription["text"] == "Hello world"
            assert transcription["language"] == "English"  # LANGUAGE_CODE_TO_NAME maps "en" -> "English"

        # Step 2: Translate
        translate_payload = {
            "text": transcription["text"],
            "source_language": "English",
            "target_language": "Spanish",
        }
        translate_response = integration_client.post(
            "/api/v1/audio/translate",
            json=translate_payload
        )
        assert translate_response.status_code == 200
        translation = translate_response.json()
        assert translation["translated_text"] == "Hola mundo"

        # Step 3: Generate TTS
        tts_payload = {
            "text": translation["translated_text"],
            "voice": "onyx",
            "model": "tts-1",
        }
        tts_response = integration_client.post("/api/v1/audio/tts", json=tts_payload)
        assert tts_response.status_code == 200
        assert tts_response.headers["content-type"] == "audio/mpeg"
        assert len(tts_response.content) > 0

    def test_transcribe_edit_translate_flow(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test workflow with manual editing: transcribe → edit → translate."""
        mock_openai_service_integration.transcribe_audio = AsyncMock(
            return_value=("Original transcription", "en")
        )
        mock_openai_service_integration.translate_text = AsyncMock(
            return_value="Transcripción editada"
        )

        async def mock_convert(input_path: object, output_path: object) -> None:
            mock_convert_to_mp3_with_file(input_path, output_path)

        with patch("backend.api.routes.v1.audio.convert_to_mp3", side_effect=mock_convert):
            # Step 1: Transcribe
            audio_file = ("test.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")
            transcribe_response = integration_client.post(
                "/api/v1/audio/transcribe",
                files={"file": audio_file}
            )
            assert transcribe_response.status_code == 200

        # Step 2: User edits transcription (client-side)
        edited_text = "Edited transcription"

        # Step 3: Translate edited text
        translate_payload = {
            "text": edited_text,
            "source_language": "English",
            "target_language": "Spanish",
        }
        translate_response = integration_client.post(
            "/api/v1/audio/translate",
            json=translate_payload
        )
        assert translate_response.status_code == 200

    def test_multiple_translations_same_source(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test translating same text to multiple languages."""
        source_text = "Hello, how are you?"
        target_languages = ["Spanish", "French", "German"]

        translations = {
            "Spanish": "Hola, ¿cómo estás?",
            "French": "Bonjour, comment allez-vous?",
            "German": "Hallo, wie geht es dir?",
        }

        # The route calls translate_text with keyword arguments
        async def mock_translate(
            text: str,
            source_language: str,
            target_language: str,
        ) -> str:
            return translations.get(target_language, "Translated")

        mock_openai_service_integration.translate_text = mock_translate

        for target_lang in target_languages:
            payload = {
                "text": source_text,
                "source_language": "English",
                "target_language": target_lang,
            }
            response = integration_client.post("/api/v1/audio/translate", json=payload)
            assert response.status_code == 200

    def test_tts_with_translated_text(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test TTS generation with translated text."""
        mock_openai_service_integration.translate_text = AsyncMock(
            return_value="Texto traducido"
        )
        mock_openai_service_integration.generate_speech = AsyncMock(
            return_value=b"fake-translated-audio"
        )

        # Step 1: Translate
        translate_response = integration_client.post(
            "/api/v1/audio/translate",
            json={
                "text": "Translated text",
                "source_language": "English",
                "target_language": "Spanish",
            }
        )
        translated_text = translate_response.json()["translated_text"]

        # Step 2: Generate TTS
        tts_response = integration_client.post(
            "/api/v1/audio/tts",
            json={
                "text": translated_text,
                "voice": "nova",
                "model": "tts-1-hd",
            }
        )
        assert tts_response.status_code == 200

    def test_health_check_before_operations(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test health check before performing operations."""
        # Check health first
        health_response = integration_client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

        # If healthy, proceed with operations
        mock_openai_service_integration.translate_text = AsyncMock(return_value="Translated")

        translate_response = integration_client.post(
            "/api/v1/audio/translate",
            json={
                "text": "Test",
                "source_language": "English",
                "target_language": "Spanish",
            }
        )
        assert translate_response.status_code == 200

    def test_error_recovery_workflow(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test error recovery in workflow."""
        # First attempt fails
        mock_openai_service_integration.translate_text = AsyncMock(
            side_effect=Exception("Temporary error")
        )

        response1 = integration_client.post(
            "/api/v1/audio/translate",
            json={
                "text": "Test",
                "source_language": "English",
                "target_language": "Spanish",
            }
        )
        assert response1.status_code == 500

        # Second attempt succeeds
        mock_openai_service_integration.translate_text = AsyncMock(
            return_value="Traducción exitosa"
        )

        response2 = integration_client.post(
            "/api/v1/audio/translate",
            json={
                "text": "Test",
                "source_language": "English",
                "target_language": "Spanish",
            }
        )
        assert response2.status_code == 200

    @pytest.mark.slow
    def test_concurrent_requests(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test handling concurrent API requests."""
        mock_openai_service_integration.translate_text = AsyncMock(
            return_value="Concurrent translation"
        )

        # Simulate concurrent requests
        def make_request(i: int) -> int:
            response = integration_client.post(
                "/api/v1/audio/translate",
                json={
                    "text": f"Test {i}",
                    "source_language": "English",
                    "target_language": "Spanish",
                }
            )
            return response.status_code

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # All requests should succeed
        assert all(status == 200 for status in results)

    def test_different_audio_formats_workflow(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test workflow with different audio formats."""
        formats = [
            ("test.mp3", "audio/mpeg"),
            ("test.ogg", "audio/ogg"),
            ("test.wav", "audio/wav"),
            ("test.m4a", "audio/x-m4a"),
        ]

        mock_openai_service_integration.transcribe_audio = AsyncMock(
            return_value=("Transcription", "en")
        )

        async def mock_convert(input_path: object, output_path: object) -> None:
            mock_convert_to_mp3_with_file(input_path, output_path)

        with patch("backend.api.routes.v1.audio.convert_to_mp3", side_effect=mock_convert):
            for filename, mime_type in formats:
                audio_file = (filename, io.BytesIO(b"fake-audio"), mime_type)
                response = integration_client.post(
                    "/api/v1/audio/transcribe",
                    files={"file": audio_file}
                )
                assert response.status_code == 200


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling across workflows."""

    def test_transcription_error_stops_workflow(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test that transcription error prevents further workflow steps."""
        mock_openai_service_integration.transcribe_audio = AsyncMock(
            side_effect=TranscriptionError("Transcription failed")
        )

        async def mock_convert(input_path: object, output_path: object) -> None:
            mock_convert_to_mp3_with_file(input_path, output_path)

        with patch("backend.api.routes.v1.audio.convert_to_mp3", side_effect=mock_convert):
            audio_file = ("test.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")
            response = integration_client.post(
                "/api/v1/audio/transcribe",
                files={"file": audio_file}
            )

        assert response.status_code == 500
        # Workflow should stop here - no translation or TTS

    def test_translation_error_allows_retry(
        self,
        integration_client: TestClient,
        mock_openai_service_integration: MockOpenAIService,
    ) -> None:
        """Test that translation error can be retried with edited text."""
        # First attempt fails
        mock_openai_service_integration.translate_text = AsyncMock(
            side_effect=TranslationError("Translation failed")
        )

        response1 = integration_client.post(
            "/api/v1/audio/translate",
            json={
                "text": "Original text",
                "source_language": "English",
                "target_language": "Spanish",
            }
        )
        assert response1.status_code == 500

        # Retry with edited text succeeds
        mock_openai_service_integration.translate_text = AsyncMock(
            return_value="Texto corregido"
        )

        response2 = integration_client.post(
            "/api/v1/audio/translate",
            json={
                "text": "Corrected text",
                "source_language": "English",
                "target_language": "Spanish",
            }
        )
        assert response2.status_code == 200
