# CLAUDE.md

Guidance for Claude Code when working with AI Dubbing Studio.

## Quick Reference

```bash
# Run the app
uv run streamlit run app.py  # http://localhost:8501

# Code quality
uv run ruff check app.py --fix  # Lint and auto-fix
uv run ruff format app.py        # Format code
uv run mypy app.py              # Type check

# Package management
uv sync                         # Install dependencies
uv add <package>                # Add new package
uv add --dev <package>          # Add dev dependency
```

**Critical:** Always use `uv` (not `pip`). Requires Python 3.13+ and FFmpeg system dependency.

## Project Overview

**Purpose:** Web app for audio dubbing via OpenAI AI (transcribe → translate → TTS)

**Stack:** Python 3.13, Streamlit, OpenAI API (GPT-4O, GPT-5.1, TTS), pydub, FFmpeg

**Architecture:** Single-file Streamlit app (app.py:144) with synchronous execution

**Entry Point:** `app.py` - contains entire UI and logic

**Data Flow:**
```
Upload Audio (OGG/MP3/WAV/M4A)
  → convert_to_mp3() (lines 32-41)
  → Transcribe with gpt-4o-transcribe (lines 71-86)
  → Manual edit UI (lines 96-102)
  → Translate with gpt-5.1 (lines 108-122)
  → TTS generation (lines 125-131)
  → Download MP3
```

## Coding Conventions

### Type Annotations (Required by mypy)
- All functions MUST have type hints for parameters and return values
- Use Python 3.10+ union syntax: `OpenAI | None` (not `Optional[OpenAI]`)
- Use `Any` for complex external types (e.g., Streamlit uploaded file)
- Add `# type: ignore[import-untyped]` for untyped third-party imports

**Example:**
```python
def validate_api_key(key: str) -> tuple[OpenAI | None, bool]:
    ...
```

### Error Handling
- Use specific exceptions: `except Exception:` (not bare `except:`)
- Display user-friendly errors: `st.error(f"Error: {e}")`
- Never expose API keys or credentials in error messages

### Streamlit Patterns
- Initialize session state at module top (lines 11-18)
- Use `st.session_state["key"]` for persistence across reruns
- One button per logical step - avoid nested conditionals
- Validate API key before any OpenAI calls

### Code Organization
- Keep single-file structure - no modules unless absolutely required
- Helper functions at top (after imports, before UI code)
- Session state initialization before any UI code
- UI code follows logical workflow order (Step 1 → 2 → 3)

## Critical Implementation Rules

### Audio Processing
1. **ALWAYS convert to MP3** using `convert_to_mp3()` before transcription
2. Supported inputs: OGG, MP3, WAV, M4A
3. Use temp files for intermediate audio processing
4. FFmpeg must be in PATH (fails silently if missing)

### API Model Selection
- **Transcription:** `gpt-4o-transcribe` (app.py:79)
- **Translation:** `gpt-5.1` (app.py:109)
- **TTS:** `tts-1` or `tts-1-hd` - user selectable (app.py:56)

### Session State Management
```python
# Key session state variables (lines 11-18)
st.session_state.transcription_text  # Stores transcription
st.session_state.translated_text     # Stores translation
st.session_state.audio_path          # Path to generated MP3
st.session_state.api_client          # Lazy-initialized OpenAI client
```

### Security
- API keys in `.env` only (never commit)
- Validate key via `validate_api_key()` (lines 23-29)
- `.env` files blocked in `.gitignore`

## File Structure

```
ai-dubbing-studio-app/
├── app.py                    # Main app (144 lines) - SINGLE SOURCE OF TRUTH
├── pyproject.toml            # Dependencies + Ruff/mypy config
├── .env                      # API key (gitignored)
├── .mcp.json                 # MCP server config (optional)
├── mcp_servers/codex/        # Code analysis MCP server (optional)
└── ai_docs/                  # OpenAI API docs (reference only)
```

## Common Tasks

### Adding Features
1. Edit `app.py` directly
2. Streamlit auto-reloads on save
3. Test in browser at http://localhost:8501
4. Run `uv run ruff check app.py --fix && uv run mypy app.py`
5. Session state persists across code reloads (but clears on browser refresh)

### Fixing Bugs
1. Check error in Streamlit UI or terminal
2. For audio issues: verify FFmpeg installation (`ffmpeg -version`)
3. For API errors: check API key in `.env`
4. For type errors: run `uv run mypy app.py`
5. Test fix immediately in browser

### Code Quality Checks
```bash
# Before committing
uv run ruff check app.py --fix  # Auto-fix linting issues
uv run ruff format app.py       # Format code
uv run mypy app.py              # Verify type safety
```

## Common Pitfalls

| Issue | Cause | Solution |
|-------|-------|----------|
| `pydub` fails silently | FFmpeg not in PATH | Install FFmpeg: `brew install ffmpeg` (macOS) |
| `audioop` import error | Python < 3.13 | Upgrade to Python 3.13+ |
| API key error on startup | Missing `.env` file | Create `.env` with `OPENAI_API_KEY=sk-...` |
| Audio not converting | Skipped `convert_to_mp3()` | Always call before transcription |
| Type errors | Missing type annotations | Add hints: `def func(x: str) -> int:` |

## Environment Setup

**Required:**
```bash
# .env file
OPENAI_API_KEY=sk-...     # Get from platform.openai.com
```

**Dependencies:**
- `streamlit` 1.52.1+ - Web UI framework
- `openai` 2.9.0+ - API client
- `pydub` 0.25.1+ - Audio conversion (needs FFmpeg)
- `audioop-lts` 0.2.2+ - Python 3.13 audio support
- `ruff` 0.14.8+ - Linter/formatter (dev)
- `mypy` 1.19.0+ - Type checker (dev)

**External:** FFmpeg (system package, not Python)

## References

- **Main workflow:** app.py:71-137
- **Audio conversion:** app.py:32-41
- **Session state init:** app.py:11-18
- **API key validation:** app.py:23-29
- **OpenAI docs:** ai_docs/ directory

## Branch Context

- **Current:** `feature/new-refactoring`
- **Main:** `main` (target for PRs)
- **Recent:** Migrated to `uv` package manager

---

**For detailed OpenAI API capabilities:** See ai_docs/ (speech-to-text, text-to-speech, GPT-5.1)
