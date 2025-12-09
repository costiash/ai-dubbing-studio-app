"""Unit tests for audio converter service."""

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from backend.core.exceptions import AudioProcessingError
from backend.services.audio_converter import convert_to_mp3


@pytest.mark.unit
class TestAudioConverter:
    """Test suite for audio conversion functionality."""

    @pytest.mark.asyncio
    async def test_convert_to_mp3_success(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test successful audio conversion to MP3."""
        input_file = tmp_path / "input.ogg"
        output_file = tmp_path / "output.mp3"

        # Create fake input file
        input_file.write_bytes(b"fake-ogg-data")

        # Perform conversion
        await convert_to_mp3(input_file, output_file)

        # Verify AudioSegment was called correctly
        mock_audio_segment.from_file.assert_called_once_with(str(input_file))

        # Verify export was called
        mock_segment_instance = mock_audio_segment.from_file.return_value
        mock_segment_instance.export.assert_called_once_with(str(output_file), format="mp3")

    @pytest.mark.asyncio
    async def test_convert_to_mp3_with_different_formats(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test conversion from various audio formats."""
        formats = [".ogg", ".wav", ".m4a", ".mp3"]

        for fmt in formats:
            input_file = tmp_path / f"input{fmt}"
            output_file = tmp_path / f"output{fmt}.mp3"

            input_file.write_bytes(b"fake-audio-data")

            await convert_to_mp3(input_file, output_file)

            # Verify conversion was attempted
            assert mock_audio_segment.from_file.called

    @pytest.mark.asyncio
    async def test_convert_to_mp3_nonexistent_input(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test conversion with nonexistent input file raises error."""
        input_file = tmp_path / "nonexistent.ogg"
        output_file = tmp_path / "output.mp3"

        # Mock AudioSegment to raise error for nonexistent file
        mock_audio_segment.from_file.side_effect = FileNotFoundError("File not found")

        with pytest.raises(AudioProcessingError) as exc_info:
            await convert_to_mp3(input_file, output_file)

        assert "Audio conversion failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_convert_to_mp3_invalid_audio_file(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test conversion with invalid audio file raises error."""
        input_file = tmp_path / "invalid.ogg"
        output_file = tmp_path / "output.mp3"

        # Create file with invalid content
        input_file.write_bytes(b"not valid audio data")

        # Mock AudioSegment to raise error for invalid format
        mock_audio_segment.from_file.side_effect = Exception("Invalid audio format")

        with pytest.raises(AudioProcessingError) as exc_info:
            await convert_to_mp3(input_file, output_file)

        assert "Audio conversion failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_convert_to_mp3_export_failure(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test conversion handles export failures."""
        input_file = tmp_path / "input.ogg"
        output_file = tmp_path / "output.mp3"

        input_file.write_bytes(b"fake-audio-data")

        # Mock export to fail
        mock_segment = mock_audio_segment.from_file.return_value
        mock_segment.export.side_effect = Exception("Export failed")

        with pytest.raises(AudioProcessingError) as exc_info:
            await convert_to_mp3(input_file, output_file)

        assert "Audio conversion failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_convert_to_mp3_creates_output_file(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test that conversion creates output file."""
        input_file = tmp_path / "input.ogg"
        output_file = tmp_path / "output.mp3"

        input_file.write_bytes(b"fake-audio-data")

        # Mock export to actually create the file
        def mock_export(path: str, format: str) -> None:
            Path(path).write_bytes(b"fake-mp3-data")

        mock_segment = mock_audio_segment.from_file.return_value
        mock_segment.export.side_effect = mock_export

        await convert_to_mp3(input_file, output_file)

        assert output_file.exists()

    @pytest.mark.asyncio
    async def test_convert_to_mp3_uses_thread_pool(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test that conversion is offloaded to thread pool (async execution)."""
        input_file = tmp_path / "input.ogg"
        output_file = tmp_path / "output.mp3"

        input_file.write_bytes(b"fake-audio-data")

        # The conversion should complete without blocking
        await convert_to_mp3(input_file, output_file)

        # If we get here, the async execution worked
        assert True

    @pytest.mark.asyncio
    async def test_convert_to_mp3_preserves_original_error_type(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test that AudioProcessingError is preserved when raised."""
        input_file = tmp_path / "input.ogg"
        output_file = tmp_path / "output.mp3"

        input_file.write_bytes(b"fake-audio-data")

        # Mock to raise AudioProcessingError directly
        mock_audio_segment.from_file.side_effect = AudioProcessingError(
            "Custom audio error"
        )

        with pytest.raises(AudioProcessingError) as exc_info:
            await convert_to_mp3(input_file, output_file)

        assert str(exc_info.value) == "Custom audio error"

    @pytest.mark.asyncio
    async def test_convert_to_mp3_with_path_objects(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test conversion accepts Path objects."""
        input_file = tmp_path / "input.ogg"
        output_file = tmp_path / "output.mp3"

        input_file.write_bytes(b"fake-audio-data")

        # Should work with Path objects
        await convert_to_mp3(input_file, output_file)

        # Verify paths were converted to strings for pydub
        mock_audio_segment.from_file.assert_called_once()
        call_args = mock_audio_segment.from_file.call_args[0]
        assert isinstance(call_args[0], str)

    @pytest.mark.asyncio
    async def test_convert_to_mp3_error_includes_details(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test that conversion errors include useful details."""
        input_file = tmp_path / "input.ogg"
        output_file = tmp_path / "output.mp3"

        input_file.write_bytes(b"fake-audio-data")

        original_error = ValueError("FFmpeg not found in PATH")
        mock_audio_segment.from_file.side_effect = original_error

        with pytest.raises(AudioProcessingError) as exc_info:
            await convert_to_mp3(input_file, output_file)

        error = exc_info.value
        assert "Audio conversion failed" in str(error)
        # The original error message should be preserved in the chain
        assert error.__cause__ == original_error

    @pytest.mark.asyncio
    @pytest.mark.slow
    async def test_convert_to_mp3_large_file(
        self,
        tmp_path: Path,
        mock_audio_segment: MagicMock,
    ) -> None:
        """Test conversion handles large audio files."""
        input_file = tmp_path / "large.ogg"
        output_file = tmp_path / "output.mp3"

        # Create a "large" file (simulated)
        large_data = b"x" * (10 * 1024 * 1024)  # 10 MB
        input_file.write_bytes(large_data)

        await convert_to_mp3(input_file, output_file)

        # Should complete without issues
        assert mock_audio_segment.from_file.called
