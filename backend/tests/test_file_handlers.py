"""Unit tests for file handler utilities."""

import io
from pathlib import Path

import pytest
from fastapi import UploadFile

from backend.core.exceptions import FileValidationError
from backend.utils.file_handlers import (
    cleanup_files,
    ensure_temp_dir,
    get_temp_file_path,
    save_upload_file,
    validate_audio_file,
)


@pytest.mark.unit
class TestFileHandlers:
    """Test suite for file handling utilities."""

    def test_ensure_temp_dir_creates_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test ensure_temp_dir creates directory if it doesn't exist."""
        temp_dir = tmp_path / "test_temp"
        monkeypatch.setattr("backend.core.config.settings.temp_dir", str(temp_dir))

        result = ensure_temp_dir()

        assert result.exists()
        assert result.is_dir()
        assert result == temp_dir

    def test_ensure_temp_dir_returns_existing_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test ensure_temp_dir works with existing directory."""
        temp_dir = tmp_path / "existing_temp"
        temp_dir.mkdir()
        monkeypatch.setattr("backend.core.config.settings.temp_dir", str(temp_dir))

        result = ensure_temp_dir()

        assert result.exists()
        assert result == temp_dir

    def test_get_temp_file_path_generates_unique_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_temp_file_path generates unique file paths."""
        temp_dir = tmp_path / "temp"
        monkeypatch.setattr("backend.core.config.settings.temp_dir", str(temp_dir))

        path1 = get_temp_file_path(suffix=".mp3")
        path2 = get_temp_file_path(suffix=".mp3")

        assert path1 != path2
        assert path1.suffix == ".mp3"
        assert path2.suffix == ".mp3"
        assert path1.parent == temp_dir
        assert path2.parent == temp_dir

    def test_get_temp_file_path_with_suffix(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_temp_file_path with various suffixes."""
        temp_dir = tmp_path / "temp"
        monkeypatch.setattr("backend.core.config.settings.temp_dir", str(temp_dir))

        mp3_path = get_temp_file_path(suffix=".mp3")
        ogg_path = get_temp_file_path(suffix=".ogg")
        no_suffix_path = get_temp_file_path()

        assert mp3_path.suffix == ".mp3"
        assert ogg_path.suffix == ".ogg"
        assert no_suffix_path.suffix == ""

    def test_get_temp_file_path_creates_parent_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test get_temp_file_path creates parent directory."""
        temp_dir = tmp_path / "new_temp"
        monkeypatch.setattr("backend.core.config.settings.temp_dir", str(temp_dir))

        path = get_temp_file_path(suffix=".mp3")

        assert path.parent.exists()
        assert path.parent.is_dir()

    def test_validate_audio_file_success(self) -> None:
        """Test validate_audio_file with valid file."""
        # In newer FastAPI versions, content_type must be set via headers parameter
        file = UploadFile(
            filename="test.mp3",
            file=io.BytesIO(b"fake data"),
            headers={"content-type": "audio/mpeg"},
        )

        # Should not raise exception
        validate_audio_file(file)

    def test_validate_audio_file_all_valid_extensions(self) -> None:
        """Test validate_audio_file accepts all valid extensions."""
        valid_extensions = [".mp3", ".ogg", ".wav", ".m4a"]

        for ext in valid_extensions:
            file = UploadFile(
                filename=f"test{ext}",
                file=io.BytesIO(b"fake data"),
            )
            validate_audio_file(file)  # Should not raise

    def test_validate_audio_file_invalid_extension(self) -> None:
        """Test validate_audio_file rejects invalid extensions."""
        file = UploadFile(
            filename="test.txt",
            file=io.BytesIO(b"fake data"),
        )

        with pytest.raises(FileValidationError) as exc_info:
            validate_audio_file(file)

        assert "Invalid file extension" in str(exc_info.value)
        assert ".txt" in str(exc_info.value)

    def test_validate_audio_file_no_filename(self) -> None:
        """Test validate_audio_file rejects file without filename."""
        file = UploadFile(
            filename=None,
            file=io.BytesIO(b"fake data"),
        )

        with pytest.raises(FileValidationError) as exc_info:
            validate_audio_file(file)

        assert "No filename provided" in str(exc_info.value)

    def test_validate_audio_file_case_insensitive_extension(self) -> None:
        """Test validate_audio_file handles case-insensitive extensions."""
        files = [
            UploadFile(filename="test.MP3", file=io.BytesIO(b"fake")),
            UploadFile(filename="test.Mp3", file=io.BytesIO(b"fake")),
            UploadFile(filename="test.OGG", file=io.BytesIO(b"fake")),
        ]

        for file in files:
            validate_audio_file(file)  # Should not raise

    def test_validate_audio_file_warns_on_mismatched_content_type(self) -> None:
        """Test validate_audio_file warns but accepts mismatched content type."""
        # In newer FastAPI versions, content_type must be set via headers parameter
        file = UploadFile(
            filename="test.mp3",
            file=io.BytesIO(b"fake data"),
            headers={"content-type": "application/octet-stream"},  # Wrong content type
        )

        # Should still pass (only extension matters)
        validate_audio_file(file)

    def test_validate_audio_file_multiple_extensions_in_filename(self) -> None:
        """Test validate_audio_file with multiple dots in filename."""
        file = UploadFile(
            filename="my.test.file.mp3",
            file=io.BytesIO(b"fake data"),
        )

        validate_audio_file(file)  # Should use last extension

    @pytest.mark.asyncio
    async def test_save_upload_file_success(self, tmp_path: Path) -> None:
        """Test save_upload_file saves file correctly."""
        content = b"test audio data content"
        file = UploadFile(
            filename="test.mp3",
            file=io.BytesIO(content),
        )

        destination = tmp_path / "saved.mp3"
        await save_upload_file(file, destination)

        assert destination.exists()
        assert destination.read_bytes() == content

    @pytest.mark.asyncio
    async def test_save_upload_file_creates_parent_dir(self, tmp_path: Path) -> None:
        """Test save_upload_file with nested destination."""
        content = b"test content"
        file = UploadFile(
            filename="test.mp3",
            file=io.BytesIO(content),
        )

        destination = tmp_path / "subdir" / "saved.mp3"
        destination.parent.mkdir(parents=True, exist_ok=True)
        await save_upload_file(file, destination)

        assert destination.exists()
        assert destination.read_bytes() == content

    @pytest.mark.asyncio
    async def test_save_upload_file_large_file(self, tmp_path: Path) -> None:
        """Test save_upload_file with large file."""
        large_content = b"x" * (5 * 1024 * 1024)  # 5 MB
        file = UploadFile(
            filename="large.mp3",
            file=io.BytesIO(large_content),
        )

        destination = tmp_path / "large.mp3"
        await save_upload_file(file, destination)

        assert destination.exists()
        assert len(destination.read_bytes()) == len(large_content)

    @pytest.mark.asyncio
    async def test_save_upload_file_overwrites_existing(self, tmp_path: Path) -> None:
        """Test save_upload_file overwrites existing file."""
        destination = tmp_path / "test.mp3"
        destination.write_bytes(b"old content")

        new_content = b"new content"
        file = UploadFile(
            filename="test.mp3",
            file=io.BytesIO(new_content),
        )

        await save_upload_file(file, destination)

        assert destination.read_bytes() == new_content

    def test_cleanup_files_deletes_existing_file(self, tmp_path: Path) -> None:
        """Test cleanup_files deletes existing files."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"

        file1.write_bytes(b"content1")
        file2.write_bytes(b"content2")

        cleanup_files(file1, file2)

        assert not file1.exists()
        assert not file2.exists()

    def test_cleanup_files_ignores_nonexistent_file(self, tmp_path: Path) -> None:
        """Test cleanup_files doesn't error on nonexistent files."""
        nonexistent = tmp_path / "nonexistent.txt"

        # Should not raise exception
        cleanup_files(nonexistent)

    def test_cleanup_files_mixed_existing_and_nonexistent(self, tmp_path: Path) -> None:
        """Test cleanup_files with mix of existing and nonexistent files."""
        existing = tmp_path / "existing.txt"
        nonexistent = tmp_path / "nonexistent.txt"

        existing.write_bytes(b"content")

        cleanup_files(existing, nonexistent)

        assert not existing.exists()

    def test_cleanup_files_accepts_string_paths(self, tmp_path: Path) -> None:
        """Test cleanup_files accepts string paths."""
        file_path = tmp_path / "test.txt"
        file_path.write_bytes(b"content")

        cleanup_files(str(file_path))

        assert not file_path.exists()

    def test_cleanup_files_accepts_path_objects(self, tmp_path: Path) -> None:
        """Test cleanup_files accepts Path objects."""
        file_path = tmp_path / "test.txt"
        file_path.write_bytes(b"content")

        cleanup_files(file_path)

        assert not file_path.exists()

    def test_cleanup_files_handles_permission_error(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test cleanup_files handles permission errors gracefully."""
        file_path = tmp_path / "protected.txt"
        file_path.write_bytes(b"content")

        # Mock unlink to raise PermissionError
        original_unlink = Path.unlink

        def mock_unlink(self: Path, missing_ok: bool = False) -> None:
            if self == file_path:
                raise PermissionError("Permission denied")
            original_unlink(self, missing_ok=missing_ok)

        monkeypatch.setattr(Path, "unlink", mock_unlink)

        # Should not raise exception, just log warning
        cleanup_files(file_path)

    def test_cleanup_files_empty_args(self) -> None:
        """Test cleanup_files with no arguments."""
        # Should not raise exception
        cleanup_files()

    def test_validate_audio_file_error_includes_details(self) -> None:
        """Test validation error includes helpful details."""
        file = UploadFile(
            filename="test.exe",
            file=io.BytesIO(b"fake data"),
        )

        with pytest.raises(FileValidationError) as exc_info:
            validate_audio_file(file)

        error = exc_info.value
        assert error.details is not None
        assert "allowed_extensions" in error.details
        assert "provided" in error.details
        assert error.details["provided"] == ".exe"
