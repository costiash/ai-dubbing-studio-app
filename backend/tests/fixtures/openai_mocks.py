"""OpenAI API mock responses for testing."""

from unittest.mock import AsyncMock, MagicMock


def create_mock_transcription_response(
    text: str = "Test transcription",
    language: str = "en",
) -> MagicMock:
    """Create a mock OpenAI transcription response.

    Args:
        text: Transcribed text
        language: Detected language code

    Returns:
        Mock transcription response object
    """
    mock_response = MagicMock()
    mock_response.text = text
    mock_response.language = language
    return mock_response


def create_mock_translation_response(
    translated_text: str = "Texto traducido",
) -> MagicMock:
    """Create a mock OpenAI chat completion response for translation.

    Args:
        translated_text: Translated text

    Returns:
        Mock chat completion response object
    """
    mock_message = MagicMock()
    mock_message.content = translated_text

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    return mock_response


def create_mock_tts_response(audio_bytes: bytes | None = None) -> MagicMock:
    """Create a mock OpenAI TTS response.

    Args:
        audio_bytes: Audio data bytes (defaults to fake data)

    Returns:
        Mock TTS response object with read() method
    """
    if audio_bytes is None:
        audio_bytes = b"fake-mp3-audio-data-" + b"x" * 1000

    mock_response = MagicMock()
    mock_response.read = MagicMock(return_value=audio_bytes)

    return mock_response


def create_mock_openai_client(
    transcription_text: str = "Test transcription",
    transcription_language: str = "en",
    translation_text: str = "Texto traducido",
    tts_audio: bytes | None = None,
) -> MagicMock:
    """Create a fully configured mock OpenAI client.

    Args:
        transcription_text: Text to return from transcription
        transcription_language: Language code for transcription
        translation_text: Text to return from translation
        tts_audio: Audio bytes to return from TTS

    Returns:
        Mock OpenAI client with all methods configured
    """
    mock_client = MagicMock()

    # Configure transcription
    mock_client.audio.transcriptions.create = AsyncMock(
        return_value=create_mock_transcription_response(
            transcription_text, transcription_language
        )
    )

    # Configure translation
    mock_client.chat.completions.create = AsyncMock(
        return_value=create_mock_translation_response(translation_text)
    )

    # Configure TTS
    mock_client.audio.speech.create = AsyncMock(
        return_value=create_mock_tts_response(tts_audio)
    )

    return mock_client


def create_mock_openai_error(
    error_type: str = "APIError",
    message: str = "OpenAI API error",
) -> Exception:
    """Create a mock OpenAI API error.

    Args:
        error_type: Type of error to simulate
        message: Error message

    Returns:
        Mock exception object
    """
    error = Exception(message)
    error.__class__.__name__ = error_type

    return error


class MockOpenAIStream:
    """Mock OpenAI streaming response."""

    def __init__(self, chunks: list[str]) -> None:
        """Initialize mock stream.

        Args:
            chunks: List of text chunks to stream
        """
        self.chunks = chunks
        self.index = 0

    async def __aiter__(self) -> "MockOpenAIStream":
        """Return async iterator.

        Returns:
            Self as async iterator
        """
        return self

    async def __anext__(self) -> str:
        """Get next chunk.

        Returns:
            Next text chunk

        Raises:
            StopAsyncIteration: When no more chunks
        """
        if self.index >= len(self.chunks):
            raise StopAsyncIteration
        chunk = self.chunks[self.index]
        self.index += 1
        return chunk
