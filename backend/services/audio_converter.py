"""Audio conversion service using pydub and FFmpeg."""

import asyncio
from functools import partial
from pathlib import Path

from pydub import AudioSegment  # type: ignore[import-untyped]

from backend.core.exceptions import AudioProcessingError
from backend.core.logging import get_logger

logger = get_logger(__name__)


def _convert_to_mp3_blocking(input_path: Path, output_path: Path) -> None:
    """Convert audio file to MP3 format (blocking operation).

    Args:
        input_path: Path to input audio file
        output_path: Path to output MP3 file

    Raises:
        AudioProcessingError: If conversion fails
    """
    try:
        logger.info(f"Converting {input_path} to MP3 at {output_path}")
        audio = AudioSegment.from_file(str(input_path))
        audio.export(str(output_path), format="mp3")
        logger.info(f"Successfully converted to MP3: {output_path}")
    except Exception as e:
        error_msg = f"Audio conversion failed: {e}"
        logger.error(error_msg)
        raise AudioProcessingError(error_msg, details={"error": str(e)}) from e


async def convert_to_mp3(input_path: Path, output_path: Path) -> None:
    """Convert audio file to MP3 format asynchronously.

    This function offloads the blocking pydub/FFmpeg operation to a thread pool
    to avoid blocking the event loop.

    Args:
        input_path: Path to input audio file
        output_path: Path to output MP3 file

    Raises:
        AudioProcessingError: If conversion fails
    """
    loop = asyncio.get_running_loop()
    convert_fn = partial(_convert_to_mp3_blocking, input_path, output_path)

    try:
        await loop.run_in_executor(None, convert_fn)
    except Exception as e:
        if isinstance(e, AudioProcessingError):
            raise
        raise AudioProcessingError(f"Audio conversion failed: {e}") from e
