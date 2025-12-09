"""Integration tests for complete API workflows."""

import io
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestCompleteWorkflows:
    """Integration tests for end-to-end workflows."""

    def test_complete_dubbing_workflow(self, client: TestClient) -> None:
        """Test complete workflow: upload → transcribe → translate → TTS."""
        # Step 1: Upload and transcribe audio
        audio_file = ("test.mp3", io.BytesIO(b"fake-audio-data"), "audio/mpeg")

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func, \
             patch("backend.api.routes.v1.audio.convert_to_mp3"):

            mock_service = MagicMock()

            # Mock transcription
            mock_service.transcribe_audio = AsyncMock(
                return_value=("Hello world", "en")
            )

            # Mock translation
            mock_service.translate_text = AsyncMock(
                return_value="Hola mundo"
            )

            # Mock TTS
            mock_service.generate_speech = AsyncMock(
                return_value=b"fake-spanish-audio"
            )

            mock_service_func.return_value = mock_service

            # Step 1: Transcribe
            transcribe_response = client.post(
                "/api/v1/audio/transcribe",
                files={"file": audio_file}
            )
            assert transcribe_response.status_code == 200
            transcription = transcribe_response.json()
            assert transcription["text"] == "Hello world"
            assert transcription["language"] == "en"

            # Step 2: Translate
            translate_payload = {
                "text": transcription["text"],
                "source_language": "English",
                "target_language": "Spanish",
            }
            translate_response = client.post(
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
            tts_response = client.post("/api/v1/audio/tts", json=tts_payload)
            assert tts_response.status_code == 200
            assert tts_response.headers["content-type"] == "audio/mpeg"
            assert len(tts_response.content) > 0

    def test_transcribe_edit_translate_flow(self, client: TestClient) -> None:
        """Test workflow with manual editing: transcribe → edit → translate."""
        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func, \
             patch("backend.api.routes.v1.audio.convert_to_mp3"):

            mock_service = MagicMock()
            mock_service.transcribe_audio = AsyncMock(
                return_value=("Original transcription", "en")
            )
            mock_service.translate_text = AsyncMock(
                return_value="Transcripción editada"
            )
            mock_service_func.return_value = mock_service

            # Step 1: Transcribe
            audio_file = ("test.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")
            transcribe_response = client.post(
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
            translate_response = client.post(
                "/api/v1/audio/translate",
                json=translate_payload
            )
            assert translate_response.status_code == 200

    def test_multiple_translations_same_source(self, client: TestClient) -> None:
        """Test translating same text to multiple languages."""
        source_text = "Hello, how are you?"
        target_languages = ["Spanish", "French", "German"]

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()

            translations = {
                "Spanish": "Hola, ¿cómo estás?",
                "French": "Bonjour, comment allez-vous?",
                "German": "Hallo, wie geht es dir?",
            }

            def mock_translate(_text: str, _source: str, target: str) -> str:
                return translations.get(target, "Translated")

            mock_service.translate_text = AsyncMock(side_effect=mock_translate)
            mock_service_func.return_value = mock_service

            for target_lang in target_languages:
                payload = {
                    "text": source_text,
                    "source_language": "English",
                    "target_language": target_lang,
                }
                response = client.post("/api/v1/audio/translate", json=payload)
                assert response.status_code == 200

    def test_tts_with_translated_text(self, client: TestClient) -> None:
        """Test TTS generation with translated text."""
        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.translate_text = AsyncMock(
                return_value="Texto traducido"
            )
            mock_service.generate_speech = AsyncMock(
                return_value=b"fake-translated-audio"
            )
            mock_service_func.return_value = mock_service

            # Step 1: Translate
            translate_response = client.post(
                "/api/v1/audio/translate",
                json={
                    "text": "Translated text",
                    "source_language": "English",
                    "target_language": "Spanish",
                }
            )
            translated_text = translate_response.json()["translated_text"]

            # Step 2: Generate TTS
            tts_response = client.post(
                "/api/v1/audio/tts",
                json={
                    "text": translated_text,
                    "voice": "nova",
                    "model": "tts-1-hd",
                }
            )
            assert tts_response.status_code == 200

    def test_health_check_before_operations(self, client: TestClient) -> None:
        """Test health check before performing operations."""
        # Check health first
        health_response = client.get("/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

        # If healthy, proceed with operations
        if health_response.json()["openai_api_configured"]:
            with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
                mock_service = MagicMock()
                mock_service.translate_text = AsyncMock(return_value="Translated")
                mock_service_func.return_value = mock_service

                translate_response = client.post(
                    "/api/v1/audio/translate",
                    json={
                        "text": "Test",
                        "source_language": "English",
                        "target_language": "Spanish",
                    }
                )
                assert translate_response.status_code == 200

    def test_error_recovery_workflow(self, client: TestClient) -> None:
        """Test error recovery in workflow."""
        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()

            # First attempt fails
            mock_service.translate_text = AsyncMock(
                side_effect=Exception("Temporary error")
            )
            mock_service_func.return_value = mock_service

            response1 = client.post(
                "/api/v1/audio/translate",
                json={
                    "text": "Test",
                    "source_language": "English",
                    "target_language": "Spanish",
                }
            )
            assert response1.status_code == 500

            # Second attempt succeeds
            mock_service.translate_text = AsyncMock(
                return_value="Traducción exitosa"
            )

            response2 = client.post(
                "/api/v1/audio/translate",
                json={
                    "text": "Test",
                    "source_language": "English",
                    "target_language": "Spanish",
                }
            )
            assert response2.status_code == 200

    @pytest.mark.slow
    def test_concurrent_requests(self, client: TestClient) -> None:
        """Test handling concurrent API requests."""
        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()
            mock_service.translate_text = AsyncMock(
                return_value="Concurrent translation"
            )
            mock_service_func.return_value = mock_service

            # Simulate concurrent requests
            import concurrent.futures

            def make_request(i: int) -> int:
                response = client.post(
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

    def test_different_audio_formats_workflow(self, client: TestClient) -> None:
        """Test workflow with different audio formats."""
        formats = [
            ("test.mp3", "audio/mpeg"),
            ("test.ogg", "audio/ogg"),
            ("test.wav", "audio/wav"),
            ("test.m4a", "audio/x-m4a"),
        ]

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func, \
             patch("backend.api.routes.v1.audio.convert_to_mp3"):

            mock_service = MagicMock()
            mock_service.transcribe_audio = AsyncMock(
                return_value=("Transcription", "en")
            )
            mock_service_func.return_value = mock_service

            for filename, mime_type in formats:
                audio_file = (filename, io.BytesIO(b"fake-audio"), mime_type)
                response = client.post(
                    "/api/v1/audio/transcribe",
                    files={"file": audio_file}
                )
                assert response.status_code == 200


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Integration tests for error handling across workflows."""

    def test_transcription_error_stops_workflow(self, client: TestClient) -> None:
        """Test that transcription error prevents further workflow steps."""
        from backend.core.exceptions import TranscriptionError

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func, \
             patch("backend.api.routes.v1.audio.convert_to_mp3"):

            mock_service = MagicMock()
            mock_service.transcribe_audio = AsyncMock(
                side_effect=TranscriptionError("Transcription failed")
            )
            mock_service_func.return_value = mock_service

            audio_file = ("test.mp3", io.BytesIO(b"fake-audio"), "audio/mpeg")
            response = client.post(
                "/api/v1/audio/transcribe",
                files={"file": audio_file}
            )

            assert response.status_code == 500
            # Workflow should stop here - no translation or TTS

    def test_translation_error_allows_retry(self, client: TestClient) -> None:
        """Test that translation error can be retried with edited text."""
        from backend.core.exceptions import TranslationError

        with patch("backend.api.routes.v1.audio.get_openai_service") as mock_service_func:
            mock_service = MagicMock()

            # First attempt fails
            mock_service.translate_text = AsyncMock(
                side_effect=TranslationError("Translation failed")
            )
            mock_service_func.return_value = mock_service

            response1 = client.post(
                "/api/v1/audio/translate",
                json={
                    "text": "Original text",
                    "source_language": "English",
                    "target_language": "Spanish",
                }
            )
            assert response1.status_code == 500

            # Retry with edited text succeeds
            mock_service.translate_text = AsyncMock(
                return_value="Texto corregido"
            )

            response2 = client.post(
                "/api/v1/audio/translate",
                json={
                    "text": "Corrected text",
                    "source_language": "English",
                    "target_language": "Spanish",
                }
            )
            assert response2.status_code == 200
