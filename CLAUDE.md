# CLAUDE.md

Project instructions for Claude Code. See @README.md for project overview.

## Quick Reference

```bash
# Backend
uv run uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload
uv run pytest backend/tests/ --cov=backend
uv run ruff check backend/ --fix && uv run ruff format backend/ && uv run mypy backend/

# Frontend
cd frontend && python server.py  # Serves on :8080
cd frontend && npm test

# Both (recommended)
./start.sh
```

## Project Context

- **Backend:** FastAPI (Python 3.13) on `localhost:8000`
- **Frontend:** Vanilla JavaScript on `localhost:8080`
- **AI Services:** OpenAI API (gpt-4o-transcribe, gpt-5.1, tts-1)
- **Package Manager:** uv (NOT pip)

See @docs/ARCHITECTURE.md for system design and @docs/API.md for endpoints.

## Critical Constraints

- **FFmpeg required:** Audio conversion fails silently without it
- **Python 3.13+:** Required for `audioop` module
- **Max upload:** 25 MB (OpenAI limit) - validate on frontend first
- **API key:** Stored in `.env`, never exposed to frontend

## Development Patterns

### Backend

- Use `uv` for all package operations (`uv sync`, `uv add`, `uv run`)
- Type annotations required: Use `str | None` syntax (NOT `Optional`)
- Custom exceptions in `backend/core/exceptions.py`
- Tests use markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.security`

### Frontend

- ES6 modules with dependency injection (constructors, not globals)
- Race condition prevention: Use `ui-lock.js` utilities
- Session persistence: `sessionManager.saveState()` after each step
- XSS prevention: Use `textContent` (NEVER `innerHTML` with user input)

### Error Handling Pattern

```python
# Backend: Always cleanup temp files
async def endpoint(background_tasks: BackgroundTasks, ...):
    temp_files = []
    try:
        result = await process(...)
        background_tasks.add_task(cleanup_files, *temp_files)
        return result
    except CustomError as e:
        background_tasks.add_task(cleanup_files, *temp_files)
        raise HTTPException(status_code=500, detail=str(e)) from e
```

```javascript
// Frontend: Always unlock UI in finally
async handleOperation() {
  if (this.isProcessing) return;
  this.isProcessing = true;
  try {
    lockUI('processing');
    await this.apiClient.operation();
  } catch (error) {
    this.uiFeedbackManager.showError(error.message);
  } finally {
    this.isProcessing = false;
    unlockUI();
  }
}
```

## Testing

- **Backend:** `uv run pytest backend/tests/` (143 tests, 86% coverage)
- **Frontend:** `cd frontend && npm test` (163 tests, 100% coverage)
- See @docs/TESTING.md for complete testing guide

## Common Pitfalls

| Issue | Solution |
|-------|----------|
| `pydub` fails silently | Install FFmpeg: `sudo apt install ffmpeg` |
| `audioop` import error | Upgrade to Python 3.13+ |
| CORS errors | Check `CORS_ORIGINS` in `.env` matches frontend port |
| Race conditions | Use `lockUI()`/`unlockUI()` from `ui-lock.js` |
| Session lost on refresh | Call `sessionManager.saveState()` after each step |

## Commit Conventions

```bash
feat: Add audio waveform visualizer
fix: Resolve race condition in file upload
chore: Update dependencies
docs: Add API documentation
test: Add integration tests for TTS endpoint
```
**NEVER ADD ATTRIBUTION FOOTER TO COMMIT MESSAGES!**

## Documentation

- @docs/API.md - REST API reference
- @docs/ARCHITECTURE.md - System design
- @docs/TESTING.md - Testing guide
- @docs/DEPLOYMENT.md - Production deployment
- @ai_docs/ - OpenAI API reference
