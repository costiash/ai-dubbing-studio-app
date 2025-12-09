"""Unit tests for custom exception classes."""

import pytest

from backend.core.exceptions import (
    AudioProcessingError,
    FileValidationError,
    TranscriptionError,
    TranslationError,
    TTSError,
)


@pytest.mark.unit
class TestCustomExceptions:
    """Test suite for custom exception classes."""

    def test_audio_processing_error_basic(self) -> None:
        """Test AudioProcessingError with basic message."""
        error = AudioProcessingError("Audio conversion failed")

        assert error.message == "Audio conversion failed"
        assert error.details == {}
        assert str(error) == "Audio conversion failed"

    def test_audio_processing_error_with_details(self) -> None:
        """Test AudioProcessingError with details dictionary."""
        details = {"file": "test.ogg", "reason": "FFmpeg not found"}
        error = AudioProcessingError("Audio conversion failed", details=details)

        assert error.message == "Audio conversion failed"
        assert error.details == details
        assert error.details["file"] == "test.ogg"
        assert error.details["reason"] == "FFmpeg not found"

    def test_transcription_error_basic(self) -> None:
        """Test TranscriptionError with basic message."""
        error = TranscriptionError("Transcription failed")

        assert error.message == "Transcription failed"
        assert error.details == {}
        assert str(error) == "Transcription failed"

    def test_transcription_error_with_details(self) -> None:
        """Test TranscriptionError with details dictionary."""
        details = {"api_error": "Rate limit exceeded", "retry_after": 60}
        error = TranscriptionError("Transcription failed", details=details)

        assert error.message == "Transcription failed"
        assert error.details == details
        assert error.details["api_error"] == "Rate limit exceeded"

    def test_translation_error_basic(self) -> None:
        """Test TranslationError with basic message."""
        error = TranslationError("Translation failed")

        assert error.message == "Translation failed"
        assert error.details == {}

    def test_translation_error_with_details(self) -> None:
        """Test TranslationError with details dictionary."""
        details = {"source_lang": "en", "target_lang": "es", "error": "Invalid language"}
        error = TranslationError("Translation failed", details=details)

        assert error.message == "Translation failed"
        assert error.details == details

    def test_tts_error_basic(self) -> None:
        """Test TTSError with basic message."""
        error = TTSError("TTS generation failed")

        assert error.message == "TTS generation failed"
        assert error.details == {}

    def test_tts_error_with_details(self) -> None:
        """Test TTSError with details dictionary."""
        details = {"voice": "onyx", "model": "tts-1", "text_length": 5000}
        error = TTSError("TTS generation failed", details=details)

        assert error.message == "TTS generation failed"
        assert error.details == details
        assert error.details["voice"] == "onyx"

    def test_file_validation_error_basic(self) -> None:
        """Test FileValidationError with basic message."""
        error = FileValidationError("Invalid file format")

        assert error.message == "Invalid file format"
        assert error.details == {}

    def test_file_validation_error_with_details(self) -> None:
        """Test FileValidationError with details dictionary."""
        details = {"filename": "test.txt", "expected": [".mp3", ".wav"], "got": ".txt"}
        error = FileValidationError("Invalid file format", details=details)

        assert error.message == "Invalid file format"
        assert error.details == details
        assert error.details["filename"] == "test.txt"

    def test_exceptions_are_exception_subclass(self) -> None:
        """Test that all custom exceptions inherit from Exception."""
        assert issubclass(AudioProcessingError, Exception)
        assert issubclass(TranscriptionError, Exception)
        assert issubclass(TranslationError, Exception)
        assert issubclass(TTSError, Exception)
        assert issubclass(FileValidationError, Exception)

    def test_exceptions_can_be_raised_and_caught(self) -> None:
        """Test that exceptions can be raised and caught properly."""
        with pytest.raises(AudioProcessingError) as exc_info:
            raise AudioProcessingError("Test error")
        assert str(exc_info.value) == "Test error"

        with pytest.raises(TranscriptionError) as exc_info:
            raise TranscriptionError("Test error")
        assert str(exc_info.value) == "Test error"

        with pytest.raises(TranslationError) as exc_info:
            raise TranslationError("Test error")
        assert str(exc_info.value) == "Test error"

        with pytest.raises(TTSError) as exc_info:
            raise TTSError("Test error")
        assert str(exc_info.value) == "Test error"

        with pytest.raises(FileValidationError) as exc_info:
            raise FileValidationError("Test error")
        assert str(exc_info.value) == "Test error"

    def test_exception_details_none_defaults_to_empty_dict(self) -> None:
        """Test that None details parameter defaults to empty dict."""
        error = AudioProcessingError("Test", details=None)
        assert error.details == {}

        error2 = TranscriptionError("Test", details=None)
        assert error2.details == {}

    def test_exception_chaining(self) -> None:
        """Test that exceptions can be chained with 'from'."""
        original_error = ValueError("Original error")

        try:
            try:
                raise original_error
            except ValueError as e:
                raise AudioProcessingError("Processing failed", details={"cause": str(e)}) from e
        except AudioProcessingError as exc:
            assert exc.message == "Processing failed"
            assert exc.details["cause"] == "Original error"
            assert exc.__cause__ == original_error

    def test_exception_with_complex_details(self) -> None:
        """Test exceptions with complex nested details."""
        details = {
            "error": "API Error",
            "metadata": {
                "request_id": "req-123",
                "timestamp": "2025-01-01T00:00:00Z",
                "endpoint": "/api/v1/audio/transcribe",
            },
            "suggestions": ["Check API key", "Verify file format"],
        }
        error = TranscriptionError("API request failed", details=details)

        assert error.details["metadata"]["request_id"] == "req-123"
        assert "Check API key" in error.details["suggestions"]
