# AI Dubbing Studio - Backend API

Production-grade FastAPI backend for audio transcription, translation, and text-to-speech using OpenAI's APIs.

## Quick Start

```bash
# Install dependencies
uv sync

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# Run development server
uv run uvicorn backend.api.main:app --reload --port 8000

# Visit API docs
open http://localhost:8000/docs
```

## Architecture

### Layered Architecture
```
Routes (HTTP) → Services (Business Logic) → External APIs (OpenAI)
              ↘ Utils (File Handling)
```

### Key Components

**API Layer** (`backend/api/`)
- `main.py` - FastAPI app, middleware, exception handlers
- `routes/health.py` - Health check endpoint
- `routes/v1/audio.py` - Audio processing endpoints

**Core Layer** (`backend/core/`)
- `config.py` - Pydantic BaseSettings (environment variables)
- `exceptions.py` - Custom exception classes
- `logging.py` - Structured logging setup

**Schemas Layer** (`backend/schemas/`)
- `audio.py` - Pydantic models for request/response validation

**Services Layer** (`backend/services/`)
- `audio_converter.py` - Audio conversion (pydub + FFmpeg)
- `openai_client.py` - OpenAI API client (AsyncOpenAI)

**Utils Layer** (`backend/utils/`)
- `file_handlers.py` - Temporary file management, validation

## Features

- **Async Operations**: All routes use `async def` with AsyncOpenAI
- **Type Safety**: Full type hints, validated with mypy
- **Auto Documentation**: OpenAPI/Swagger docs at `/docs`
- **Error Handling**: Custom exceptions with detailed error responses
- **File Management**: Automatic cleanup via BackgroundTasks
- **CORS Support**: Configured for frontend integration
- **Structured Logging**: Configurable log levels

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/api/v1/audio/transcribe` | Transcribe audio to text |
| POST | `/api/v1/audio/translate` | Translate text |
| POST | `/api/v1/audio/tts` | Text-to-speech |

See [API_CONTRACT.md](../API_CONTRACT.md) for full documentation.

## Configuration

Environment variables (`.env` file):

```bash
# Required
OPENAI_API_KEY=sk-...

# Optional (defaults shown)
DEBUG=false
TEMP_DIR=/tmp/ai-dubbing-studio
TRANSCRIPTION_MODEL=gpt-4o-transcribe
TRANSLATION_MODEL=gpt-5.1
TTS_MODEL_DEFAULT=tts-1
```

## Development

### Code Quality

```bash
# Lint and auto-fix
uv run ruff check backend/ --fix

# Format code
uv run ruff format backend/

# Type check
uv run mypy backend/
```

### Running Tests

```bash
# Start server
uv run uvicorn backend.api.main:app --reload --port 8000

# Test health endpoint
curl http://localhost:8000/health

# Test transcription (requires audio file)
curl -X POST http://localhost:8000/api/v1/audio/transcribe \
  -F "file=@test_audio.mp3"
```

## Deployment

### Production Server

```bash
# Install production dependencies
uv sync

# Run with Gunicorn + Uvicorn workers
gunicorn backend.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 120
```

### Docker (Future)

```dockerfile
FROM python:3.13-slim

# Install FFmpeg (required for pydub)
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Dependencies

**Core:**
- `fastapi>=0.115.0` - Web framework
- `uvicorn[standard]>=0.32.0` - ASGI server
- `pydantic-settings>=2.6.0` - Configuration management
- `python-multipart>=0.0.18` - File upload support

**OpenAI:**
- `openai>=2.9.0` - OpenAI Python SDK (async support)

**Audio Processing:**
- `pydub>=0.25.1` - Audio conversion
- `audioop-lts>=0.2.2` - Python 3.13 audio support
- **System:** FFmpeg (must be installed separately)

**Development:**
- `mypy>=1.19.0` - Type checking
- `ruff>=0.14.8` - Linting and formatting

## Project Structure

```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── dependencies.py      # Dependency injection
│   └── routes/
│       ├── __init__.py
│       ├── health.py        # GET /health
│       └── v1/
│           ├── __init__.py
│           └── audio.py     # POST /api/v1/audio/*
├── core/
│   ├── __init__.py
│   ├── config.py            # Settings (Pydantic BaseSettings)
│   ├── exceptions.py        # Custom exceptions
│   └── logging.py           # Logging setup
├── schemas/
│   ├── __init__.py
│   └── audio.py             # Pydantic models
├── services/
│   ├── __init__.py
│   ├── audio_converter.py   # Audio conversion (pydub)
│   └── openai_client.py     # OpenAI API client
├── utils/
│   ├── __init__.py
│   └── file_handlers.py     # File validation, temp files
└── README.md                # This file
```

## Design Decisions

### Why Async?
- OpenAI SDK supports async via `AsyncOpenAI`
- Non-blocking I/O for better concurrency
- Offloads CPU-bound tasks (pydub) to thread pool

### Why No Database?
- No persistent state required
- All data flows through external APIs
- Temporary files are cleaned up automatically

### Why Services Layer (No Repositories)?
- Repositories pattern typically abstracts database access
- Services directly call external APIs (OpenAI)
- Simpler architecture for this use case

### Temporary File Handling
- Uploaded files saved to `/tmp/ai-dubbing-studio`
- Converted to MP3 before sending to OpenAI
- Background tasks clean up files after response
- Temp directory created on startup

## Troubleshooting

### FFmpeg Not Found
```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Verify installation
ffmpeg -version
```

### OpenAI API Key Issues
```bash
# Check if key is set
echo $OPENAI_API_KEY

# Test API access
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Type Errors
```bash
# Run mypy to see all errors
uv run mypy backend/

# Common issue: import untyped libraries
# Solution: Add # type: ignore[import-untyped]
```

## Next Steps

This backend is ready for Phase 2 (UI refactoring) and Phase 3 (frontend development).

**Phase 2** will:
- Refactor Streamlit app to use this API
- Separate UI from business logic
- Use HTTP requests instead of direct OpenAI calls

**Phase 3** will:
- Build modern frontend (React/Next.js)
- Integrate with this backend via REST API
- Provide improved UX/UI

See [API_CONTRACT.md](../API_CONTRACT.md) for integration details.
