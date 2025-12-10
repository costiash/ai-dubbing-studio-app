---
paths: backend/**/*.py
---

# Backend Python Rules

## Code Style

- Type annotations required for all functions
- Use `str | None` syntax (Python 3.10+), NOT `Optional[str]`
- Import order: stdlib, third-party, local (Ruff handles this)
- Use `async def` for I/O operations

## Exceptions

Use specific exceptions from `backend/core/exceptions.py`:
- `FileValidationError` - Invalid file format/size
- `AudioProcessingError` - FFmpeg/pydub failures
- `TranscriptionError` - OpenAI transcription failures
- `TranslationError` - OpenAI translation failures
- `TTSError` - OpenAI TTS failures

Always chain exceptions: `raise CustomError(...) from e`

## Logging

```python
from backend.core.logging import get_logger
logger = get_logger(__name__)

logger.info(f"Processing: {filename}")
logger.error(f"Failed: {error}", exc_info=True)
```

## Testing

- Unit tests: `@pytest.mark.unit`
- Integration tests: `@pytest.mark.integration`
- Security tests: `@pytest.mark.security`
- Mock OpenAI calls using fixtures in `backend/tests/fixtures/openai_mocks.py`

## API Routes Pattern

```python
async def endpoint(background_tasks: BackgroundTasks, ...):
    temp_files = []
    try:
        # 1. Validate input
        # 2. Process
        # 3. Schedule cleanup
        background_tasks.add_task(cleanup_files, *temp_files)
        return result
    except CustomError as e:
        if temp_files:
            background_tasks.add_task(cleanup_files, *temp_files)
        raise HTTPException(status_code=500, detail=str(e)) from e
```

## Quality Commands

```bash
uv run ruff check backend/ --fix   # Lint
uv run ruff format backend/        # Format
uv run mypy backend/               # Type check
uv run pytest backend/tests/ -v    # Test
```
