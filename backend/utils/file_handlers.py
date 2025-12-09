"""Utilities for handling temporary files."""

import uuid
from pathlib import Path

from fastapi import UploadFile

from backend.core.config import settings
from backend.core.exceptions import FileValidationError
from backend.core.logging import get_logger

logger = get_logger(__name__)


def ensure_temp_dir() -> Path:
    """Ensure temporary directory exists.

    Returns:
        Path to temporary directory
    """
    temp_path = Path(settings.temp_dir)
    temp_path.mkdir(parents=True, exist_ok=True)
    return temp_path


def get_temp_file_path(suffix: str = "") -> Path:
    """Generate a unique temporary file path.

    Args:
        suffix: File suffix (e.g., '.mp3')

    Returns:
        Path to temporary file
    """
    temp_dir = ensure_temp_dir()
    unique_name = f"{uuid.uuid4()}{suffix}"
    return temp_dir / unique_name


def validate_audio_file(file: UploadFile) -> None:
    """Validate uploaded audio file.

    Args:
        file: Uploaded file
        max_size: Maximum file size in bytes (defaults to settings.max_upload_size)

    Raises:
        FileValidationError: If file validation fails
    """
    if not file.filename:
        raise FileValidationError("No filename provided")

    # Check file extension
    file_ext = Path(file.filename).suffix.lower()
    valid_extensions = [".mp3", ".ogg", ".wav", ".m4a"]
    if file_ext not in valid_extensions:
        raise FileValidationError(
            f"Invalid file extension '{file_ext}'. Allowed: {', '.join(valid_extensions)}",
            details={"allowed_extensions": valid_extensions, "provided": file_ext},
        )

    # Check content type (if provided)
    if file.content_type and file.content_type not in settings.allowed_audio_formats:
        logger.warning(
            f"Content type '{file.content_type}' not in allowed list, "
            f"but extension '{file_ext}' is valid - proceeding"
        )

    # Size validation would require reading the file
    # We'll rely on FastAPI's max_upload_size configuration
    logger.info(f"Validated audio file: {file.filename} ({file.content_type})")


async def save_upload_file(file: UploadFile, destination: Path) -> None:
    """Save uploaded file to destination.

    Args:
        file: Uploaded file
        destination: Destination path

    Raises:
        Exception: If file save fails
    """
    try:
        content = await file.read()
        with open(destination, "wb") as f:
            f.write(content)
        logger.info(f"Saved uploaded file to {destination}")
    except Exception as e:
        logger.error(f"Failed to save file to {destination}: {e}")
        raise


def cleanup_files(*paths: Path | str) -> None:
    """Clean up temporary files.

    Args:
        *paths: Paths to files to delete
    """
    for path in paths:
        try:
            path_obj = Path(path)
            if path_obj.exists():
                path_obj.unlink()
                logger.debug(f"Deleted temporary file: {path_obj}")
        except Exception as e:
            logger.warning(f"Failed to delete temporary file {path}: {e}")
