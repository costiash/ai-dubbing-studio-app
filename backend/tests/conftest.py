"""Pytest configuration and shared fixtures for backend tests."""

import io
import tempfile
from pathlib import Path
from typing import Any, BinaryIO, Generator
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.core.config import Settings, get_settings
from backend.services.openai_client import OpenAIService


@pytest.fixture
def test_settings() -> Settings:
    """Create test settings with safe defaults.

    Returns:
        Settings instance configured for testing
    """
    return Settings(
        openai_api_key="sk-test-key-12345",
        app_name="AI Dubbing Studio API (Test)",
        debug=True,
        api_version="v1",
        max_upload_size=26214400,
        temp_dir=tempfile.gettempdir() + "/ai-dubbing-studio-test",
        transcription_model="gpt-4o-transcribe",
        translation_model="gpt-5.1",
        tts_model_default="tts-1",
        tts_voice_default="onyx",
        cors_origins=["http://localhost:3000"],
        cors_allow_credentials=True,
    )


@pytest.fixture
def client(test_settings: Settings) -> Generator[TestClient, None, None]:
    """Create FastAPI test client with overridden test settings.

    This allows tests to run without requiring OPENAI_API_KEY in environment.

    Args:
        test_settings: Test settings fixture

    Yields:
        TestClient instance for making API requests
    """
    # Override settings dependency for testing
    app.dependency_overrides[get_settings] = lambda: test_settings

    with TestClient(app) as test_client:
        yield test_client

    # Clean up override after test
    app.dependency_overrides.clear()


@pytest.fixture
def mock_openai_response_transcribe() -> dict[str, Any]:
    """Mock OpenAI transcription response data.

    Returns:
        Dictionary representing successful transcription response
    """
    return {
        "text": "This is a test transcription.",
        "language": "en",
    }


@pytest.fixture
def mock_openai_response_translate() -> dict[str, Any]:
    """Mock OpenAI translation response data.

    Returns:
        Dictionary representing successful translation response
    """
    return {
        "translated_text": "Esto es una prueba de traducción.",
        "source_language": "English",
        "target_language": "Spanish",
    }


@pytest.fixture
def mock_openai_response_tts() -> bytes:
    """Mock OpenAI TTS response data.

    Returns:
        Bytes representing fake MP3 audio data
    """
    return b"fake-mp3-audio-data-" + b"x" * 1000


@pytest.fixture
def mock_openai_client(
    mock_openai_response_transcribe: dict[str, Any],
    mock_openai_response_translate: dict[str, Any],
    mock_openai_response_tts: bytes,
) -> MagicMock:
    """Create a mock OpenAI client with pre-configured responses.

    Args:
        mock_openai_response_transcribe: Mock transcription response
        mock_openai_response_translate: Mock translation response
        mock_openai_response_tts: Mock TTS response

    Returns:
        Mock OpenAI client configured for testing
    """
    mock_client = MagicMock()

    # Mock transcription
    mock_transcribe_response = MagicMock()
    mock_transcribe_response.text = mock_openai_response_transcribe["text"]
    mock_transcribe_response.language = mock_openai_response_transcribe["language"]
    mock_client.audio.transcriptions.create = AsyncMock(
        return_value=mock_transcribe_response
    )

    # Mock translation (chat completion)
    mock_translate_message = MagicMock()
    mock_translate_message.content = mock_openai_response_translate["translated_text"]
    mock_translate_choice = MagicMock()
    mock_translate_choice.message = mock_translate_message
    mock_translate_response = MagicMock()
    mock_translate_response.choices = [mock_translate_choice]
    mock_client.chat.completions.create = AsyncMock(
        return_value=mock_translate_response
    )

    # Mock TTS
    mock_tts_response = MagicMock()
    mock_tts_response.read = MagicMock(return_value=mock_openai_response_tts)
    mock_client.audio.speech.create = AsyncMock(
        return_value=mock_tts_response
    )

    return mock_client


@pytest.fixture
def mock_openai_service(mock_openai_client: MagicMock) -> OpenAIService:
    """Create OpenAI service with mocked client.

    Args:
        mock_openai_client: Mock OpenAI client

    Returns:
        OpenAI service instance with mocked client
    """
    service = OpenAIService(api_key="sk-test-key-12345")
    service.client = mock_openai_client
    return service


@pytest.fixture
def sample_audio_file() -> BinaryIO:
    """Create a sample audio file for testing.

    Returns:
        BytesIO object containing fake audio data
    """
    content = b"fake-audio-data-" + b"x" * 500
    return io.BytesIO(content)


@pytest.fixture
def sample_mp3_file(tmp_path: Path) -> Path:
    """Create a sample MP3 file on disk.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to the created MP3 file
    """
    mp3_file = tmp_path / "sample.mp3"
    mp3_file.write_bytes(b"fake-mp3-audio-data-" + b"x" * 1000)
    return mp3_file


@pytest.fixture
def sample_ogg_file(tmp_path: Path) -> Path:
    """Create a sample OGG file on disk.

    Args:
        tmp_path: Pytest temporary directory fixture

    Returns:
        Path to the created OGG file
    """
    ogg_file = tmp_path / "sample.ogg"
    ogg_file.write_bytes(b"OggS" + b"fake-ogg-audio-data-" + b"x" * 1000)
    return ogg_file


@pytest.fixture
def sample_text_english() -> str:
    """Sample English text for testing.

    Returns:
        English text string
    """
    return "Hello, this is a test of the AI dubbing studio application."


@pytest.fixture
def sample_text_spanish() -> str:
    """Sample Spanish text for testing.

    Returns:
        Spanish text string
    """
    return "Hola, esta es una prueba de la aplicación de estudio de doblaje de IA."


@pytest.fixture(autouse=True)
def cleanup_temp_files(tmp_path: Path) -> Generator[None, None, None]:
    """Automatically clean up temporary files after each test.

    Args:
        tmp_path: Pytest temporary directory fixture

    Yields:
        None (performs cleanup after test)
    """
    yield
    # Cleanup happens automatically with tmp_path fixture
    # This is here as a hook for custom cleanup if needed


@pytest.fixture
def mock_audio_segment(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Mock pydub AudioSegment for audio conversion tests.

    Args:
        monkeypatch: Pytest monkeypatch fixture

    Returns:
        Mock AudioSegment class
    """
    mock_segment = MagicMock()
    mock_segment.export = MagicMock()

    mock_audio_segment_class = MagicMock(return_value=mock_segment)
    mock_audio_segment_class.from_file = MagicMock(return_value=mock_segment)

    monkeypatch.setattr("backend.services.audio_converter.AudioSegment", mock_audio_segment_class)

    return mock_audio_segment_class


@pytest.fixture
def large_text() -> str:
    """Generate a large text for testing size limits.

    Returns:
        Large text string
    """
    return "This is a test sentence. " * 1000


@pytest.fixture
def special_chars_text() -> str:
    """Text with special characters for testing.

    Returns:
        Text containing special characters
    """
    return "Hello! ¿Cómo estás? 你好 Привет мир 🎉 <script>alert('xss')</script>"


@pytest.fixture
def empty_text() -> str:
    """Empty text for testing validation.

    Returns:
        Empty string
    """
    return ""


# NOTE: This fixture was removed because it conflicts with manual patches in tests
# Tests that need custom convert_to_mp3 behavior (like error testing) would fail
# The original test suite works fine without this
