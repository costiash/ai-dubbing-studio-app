"""Unit tests for OpenAI client service."""

from typing import BinaryIO
from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.core.exceptions import TranscriptionError, TranslationError, TTSError
from backend.services.openai_client import OpenAIService, get_openai_service
from backend.tests.fixtures.openai_mocks import (
    create_mock_openai_client,
    create_mock_openai_error,
)


@pytest.mark.unit
class TestOpenAIService:
    """Test suite for OpenAI service."""

    def test_init_with_api_key(self) -> None:
        """Test OpenAI service initialization with API key."""
        service = OpenAIService(api_key="sk-test-key-12345")

        assert service.api_key == "sk-test-key-12345"
        assert service.client is not None

    def test_init_without_api_key_uses_settings(self) -> None:
        """Test OpenAI service initialization uses settings if no key provided."""
        service = OpenAIService()

        assert service.api_key is not None
        assert service.client is not None

    @pytest.mark.asyncio
    async def test_transcribe_audio_success(
        self,
        sample_audio_file: BinaryIO,
    ) -> None:
        """Test successful audio transcription."""
        # Create service with mocked client
        service = OpenAIService(api_key="sk-test-key")
        mock_client = create_mock_openai_client(
            transcription_text="Hello world",
            transcription_language="en",
        )
        service.client = mock_client

        # Execute transcription
        text, language = await service.transcribe_audio(sample_audio_file)

        # Verify results
        assert text == "Hello world"
        assert language == "en"
        mock_client.audio.transcriptions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_transcribe_audio_with_language_hint(
        self,
        sample_audio_file: BinaryIO,
    ) -> None:
        """Test transcription with language hint."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = create_mock_openai_client()
        service.client = mock_client

        await service.transcribe_audio(sample_audio_file, language="es")

        # Verify language parameter was passed
        call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
        assert call_kwargs["language"] == "es"

    @pytest.mark.asyncio
    async def test_transcribe_audio_handles_dict_response(
        self,
        sample_audio_file: BinaryIO,
    ) -> None:
        """Test transcription handles dict-style response."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = MagicMock()

        # Mock response as dict (some API versions return dict)
        mock_client.audio.transcriptions.create = AsyncMock(
            return_value={"text": "Test text", "language": "fr"}
        )
        service.client = mock_client

        text, language = await service.transcribe_audio(sample_audio_file)

        assert text == "Test text"
        assert language == "fr"

    @pytest.mark.asyncio
    async def test_transcribe_audio_error(
        self,
        sample_audio_file: BinaryIO,
    ) -> None:
        """Test transcription error handling."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = MagicMock()
        mock_client.audio.transcriptions.create = AsyncMock(
            side_effect=create_mock_openai_error("APIError", "Transcription failed")
        )
        service.client = mock_client

        with pytest.raises(TranscriptionError) as exc_info:
            await service.transcribe_audio(sample_audio_file)

        assert "Transcription failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_translate_text_success(self) -> None:
        """Test successful text translation."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = create_mock_openai_client(
            translation_text="Hola, ¿cómo estás?"
        )
        service.client = mock_client

        result = await service.translate_text(
            text="Hello, how are you?",
            source_language="English",
            target_language="Spanish",
        )

        assert result == "Hola, ¿cómo estás?"
        mock_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_translate_text_with_correct_prompt(self) -> None:
        """Test translation sends correct prompt to API."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = create_mock_openai_client()
        service.client = mock_client

        await service.translate_text(
            text="Test text",
            source_language="English",
            target_language="French",
        )

        # Verify the prompt structure
        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        messages = call_kwargs["messages"]

        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert "English" in messages[0]["content"]
        assert "French" in messages[0]["content"]
        assert messages[1]["role"] == "user"
        assert messages[1]["content"] == "Test text"

    @pytest.mark.asyncio
    async def test_translate_text_temperature_setting(self) -> None:
        """Test translation uses correct temperature for consistency."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = create_mock_openai_client()
        service.client = mock_client

        await service.translate_text(
            text="Test",
            source_language="English",
            target_language="Spanish",
        )

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert call_kwargs["temperature"] == 0.3

    @pytest.mark.asyncio
    async def test_translate_text_empty_response_error(self) -> None:
        """Test translation handles empty response."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = MagicMock()

        # Mock empty response
        mock_message = MagicMock()
        mock_message.content = None
        mock_choice = MagicMock()
        mock_choice.message = mock_message
        mock_response = MagicMock()
        mock_response.choices = [mock_choice]

        mock_client.chat.completions.create = AsyncMock(return_value=mock_response)
        service.client = mock_client

        with pytest.raises(TranslationError) as exc_info:
            await service.translate_text("Test", "English", "Spanish")

        assert "empty response" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_translate_text_api_error(self) -> None:
        """Test translation error handling."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(
            side_effect=create_mock_openai_error("APIError", "Translation failed")
        )
        service.client = mock_client

        with pytest.raises(TranslationError) as exc_info:
            await service.translate_text("Test", "English", "Spanish")

        assert "Translation failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_speech_success(self) -> None:
        """Test successful TTS generation."""
        service = OpenAIService(api_key="sk-test-key")
        expected_audio = b"fake-audio-data-123"
        mock_client = create_mock_openai_client(tts_audio=expected_audio)
        service.client = mock_client

        audio_bytes = await service.generate_speech(
            text="Hello world",
            voice="onyx",
            model="tts-1",
        )

        assert audio_bytes == expected_audio
        mock_client.audio.speech.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_speech_with_custom_voice(self) -> None:
        """Test TTS with custom voice parameter."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = create_mock_openai_client()
        service.client = mock_client

        await service.generate_speech(
            text="Test",
            voice="nova",
            model="tts-1-hd",
        )

        call_kwargs = mock_client.audio.speech.create.call_args.kwargs
        assert call_kwargs["voice"] == "nova"
        assert call_kwargs["model"] == "tts-1-hd"
        assert call_kwargs["input"] == "Test"

    @pytest.mark.asyncio
    async def test_generate_speech_returns_bytes(self) -> None:
        """Test TTS returns audio bytes."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = create_mock_openai_client()
        service.client = mock_client

        result = await service.generate_speech("Test", "onyx", "tts-1")

        assert isinstance(result, bytes)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_generate_speech_error(self) -> None:
        """Test TTS error handling."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = MagicMock()
        mock_client.audio.speech.create = AsyncMock(
            side_effect=create_mock_openai_error("APIError", "TTS failed")
        )
        service.client = mock_client

        with pytest.raises(TTSError) as exc_info:
            await service.generate_speech("Test", "onyx", "tts-1")

        assert "TTS" in str(exc_info.value)

    def test_get_openai_service_singleton(self) -> None:
        """Test get_openai_service returns singleton instance."""
        # Reset global instance
        import backend.services.openai_client
        backend.services.openai_client._openai_service = None

        service1 = get_openai_service()
        service2 = get_openai_service()

        assert service1 is service2

    @pytest.mark.asyncio
    async def test_transcribe_with_model_from_settings(
        self,
        sample_audio_file: BinaryIO,
    ) -> None:
        """Test transcription uses model from settings."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = create_mock_openai_client()
        service.client = mock_client

        await service.transcribe_audio(sample_audio_file)

        call_kwargs = mock_client.audio.transcriptions.create.call_args.kwargs
        assert "model" in call_kwargs
        # Model comes from settings.transcription_model

    @pytest.mark.asyncio
    async def test_translate_with_model_from_settings(self) -> None:
        """Test translation uses model from settings."""
        service = OpenAIService(api_key="sk-test-key")
        mock_client = create_mock_openai_client()
        service.client = mock_client

        await service.translate_text("Test", "English", "Spanish")

        call_kwargs = mock_client.chat.completions.create.call_args.kwargs
        assert "model" in call_kwargs
        # Model comes from settings.translation_model
