# API Contract - AI Dubbing Studio Backend

**Version:** v1
**Base URL:** `http://localhost:8000`
**Documentation:** `http://localhost:8000/docs` (Swagger UI)
**OpenAPI Spec:** `http://localhost:8000/openapi.json`

## Overview

This document defines the API contract for the AI Dubbing Studio backend, a FastAPI-based service that provides audio transcription, text translation, and text-to-speech capabilities using OpenAI's API.

## Table of Contents

- [Authentication](#authentication)
- [Endpoints](#endpoints)
  - [Health Check](#get-health)
  - [Transcribe Audio](#post-apiv1audiotranscribe)
  - [Translate Text](#post-apiv1audiotranslate)
  - [Text-to-Speech](#post-apiv1audiotts)
- [Data Models](#data-models)
- [Error Handling](#error-handling)
- [Rate Limits](#rate-limits)
- [CORS Configuration](#cors-configuration)

---

## Authentication

**Current:** No authentication required (development mode)

**Production Recommendation:** Implement API key authentication or OAuth2 before deployment.

```http
Authorization: Bearer <api-key>
```

---

## Endpoints

### GET /health

Health check endpoint to verify API and OpenAI configuration status.

**Request:**
```http
GET /health HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
```json
{
  "status": "healthy",
  "openai_api_configured": true,
  "version": "v1"
}
```

**Response Schema:**
- `status` (string): Health status ("healthy" or "unhealthy")
- `openai_api_configured` (boolean): Whether OpenAI API key is configured
- `version` (string): API version

---

### POST /api/v1/audio/transcribe

Transcribe audio file to text using OpenAI's `gpt-4o-transcribe` model.

**Supported Audio Formats:** OGG, MP3, WAV, M4A

**Request:**
```http
POST /api/v1/audio/transcribe HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="audio.mp3"
Content-Type: audio/mpeg

[Binary audio data]
------WebKitFormBoundary--
```

**Request Parameters:**
- `file` (file, required): Audio file to transcribe
  - Max size: 25 MB (OpenAI limit)
  - Allowed extensions: `.ogg`, `.mp3`, `.wav`, `.m4a`
  - Content types: `audio/mpeg`, `audio/ogg`, `audio/wav`, `audio/x-m4a`, `audio/mp4`

**Response (200 OK):**
```json
{
  "text": "שלום, זהו דוגמה של תמלול אודיו.",
  "language": "Hebrew"
}
```

**Response Schema:**
- `text` (string, required): Transcribed text from audio
- `language` (string, nullable): Detected or specified language

**Errors:**

**400 Bad Request** - Invalid file format or validation error
```json
{
  "detail": "Invalid file extension '.txt'. Allowed: .mp3, .ogg, .wav, .m4a",
  "error_code": "FILE_VALIDATION_ERROR",
  "errors": {
    "allowed_extensions": [".mp3", ".ogg", ".wav", ".m4a"],
    "provided": ".txt"
  }
}
```

**413 Payload Too Large** - File exceeds 25 MB
```json
{
  "detail": "File too large",
  "error_code": "FILE_TOO_LARGE"
}
```

**500 Internal Server Error** - Transcription failed
```json
{
  "detail": "Transcription failed: <error message>",
  "error_code": "TRANSCRIPTION_ERROR",
  "errors": {
    "error": "<detailed error>"
  }
}
```

**Process Flow:**
1. Validate uploaded file (format, extension)
2. Save to temporary directory (`/tmp/ai-dubbing-studio`)
3. Convert to MP3 using pydub + FFmpeg (async via thread pool)
4. Send to OpenAI transcription API
5. Return transcribed text
6. Clean up temporary files (background task)

---

### POST /api/v1/audio/translate

Translate text from one language to another using OpenAI's `gpt-5.1` model.

**Request:**
```http
POST /api/v1/audio/translate HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "text": "שלום, זהו דוגמה של תרגום טקסט.",
  "source_language": "Hebrew",
  "target_language": "Russian"
}
```

**Request Schema:**
```typescript
{
  text: string;             // Text to translate (1-50,000 characters)
  source_language: string;  // Source language name (e.g., "Hebrew", "English")
  target_language: string;  // Target language name (e.g., "Russian", "Spanish")
}
```

**Response (200 OK):**
```json
{
  "translated_text": "Привет, это пример перевода текста.",
  "source_language": "Hebrew",
  "target_language": "Russian"
}
```

**Response Schema:**
- `translated_text` (string, required): Translated text
- `source_language` (string, required): Source language (echoed from request)
- `target_language` (string, required): Target language (echoed from request)

**Errors:**

**422 Unprocessable Entity** - Validation error
```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "text"],
      "msg": "String should have at least 1 character",
      "input": "",
      "ctx": {"min_length": 1}
    }
  ]
}
```

**500 Internal Server Error** - Translation failed
```json
{
  "detail": "Translation failed: <error message>",
  "error_code": "TRANSLATION_ERROR",
  "errors": {
    "error": "<detailed error>"
  }
}
```

**Notes:**
- Uses GPT-5.1 with temperature=0.3 for consistent translations
- System prompt instructs model to provide natural, fluent translations
- Returns only translated text (no explanations)

---

### POST /api/v1/audio/tts

Generate speech from text using OpenAI's Text-to-Speech API.

**Request:**
```http
POST /api/v1/audio/tts HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "text": "Привет, это пример синтеза речи.",
  "voice": "onyx",
  "model": "tts-1"
}
```

**Request Schema:**
```typescript
{
  text: string;   // Text to convert to speech (1-4,096 characters)
  voice?: string; // Voice name (default: "onyx")
  model?: string; // TTS model (default: "tts-1")
}
```

**Available Voices:**
- `alloy` - Neutral, balanced
- `echo` - Male, clear
- `fable` - British accent
- `onyx` - Deep, authoritative (default)
- `nova` - Female, energetic
- `shimmer` - Female, warm

**Available Models:**
- `tts-1` - Standard quality, faster (default)
- `tts-1-hd` - High definition, slower

**Response (200 OK):**
```http
HTTP/1.1 200 OK
Content-Type: audio/mpeg
Content-Disposition: attachment; filename=speech.mp3

[Binary MP3 data]
```

**Response:**
- Binary audio file in MP3 format
- Content-Type: `audio/mpeg`
- Content-Disposition: `attachment; filename=speech.mp3`

**Errors:**

**422 Unprocessable Entity** - Validation error
```json
{
  "detail": [
    {
      "type": "string_too_long",
      "loc": ["body", "text"],
      "msg": "String should have at most 4096 characters",
      "input": "<very long text>",
      "ctx": {"max_length": 4096}
    }
  ]
}
```

**500 Internal Server Error** - TTS generation failed
```json
{
  "detail": "TTS generation failed: <error message>",
  "error_code": "TTS_ERROR",
  "errors": {
    "error": "<detailed error>"
  }
}
```

**Notes:**
- Audio is returned as binary MP3 data
- Suitable for direct playback or download
- Response is buffered (not streamed) for simplicity

---

## Data Models

### TranscribeResponse
```typescript
{
  text: string;         // Transcribed text (required)
  language: string | null;  // Detected language (optional)
}
```

### TranslateRequest
```typescript
{
  text: string;             // 1-50,000 characters (required)
  source_language: string;  // 1-50 characters (required)
  target_language: string;  // 1-50 characters (required)
}
```

### TranslateResponse
```typescript
{
  translated_text: string;  // Translated text (required)
  source_language: string;  // Source language (required)
  target_language: string;  // Target language (required)
}
```

### TTSRequest
```typescript
{
  text: string;    // 1-4,096 characters (required)
  voice?: string;  // Default: "onyx"
  model?: string;  // Default: "tts-1"
}
```

### HealthResponse
```typescript
{
  status: string;                // "healthy" or "unhealthy"
  openai_api_configured: boolean; // API key configured
  version: string;               // API version
}
```

### ErrorResponse
```typescript
{
  detail: string;                  // Human-readable error message
  error_code?: string;             // Machine-readable code
  errors?: Record<string, any>;    // Additional error details
}
```

---

## Error Handling

### HTTP Status Codes

- **200 OK** - Successful request
- **400 Bad Request** - Invalid input (file validation, etc.)
- **413 Payload Too Large** - File exceeds size limit
- **422 Unprocessable Entity** - Pydantic validation error
- **500 Internal Server Error** - Server error (transcription, translation, TTS failures)

### Error Response Format

All errors follow this structure:

```json
{
  "detail": "Human-readable error message",
  "error_code": "MACHINE_READABLE_CODE",
  "errors": {
    "additional": "context"
  }
}
```

### Error Codes

| Code | Description |
|------|-------------|
| `FILE_VALIDATION_ERROR` | Invalid file format or extension |
| `AUDIO_PROCESSING_ERROR` | Audio conversion failed (pydub/FFmpeg) |
| `TRANSCRIPTION_ERROR` | OpenAI transcription API failed |
| `TRANSLATION_ERROR` | OpenAI translation API failed |
| `TTS_ERROR` | OpenAI TTS API failed |
| `HTTP_ERROR` | Generic HTTP exception |

---

## Rate Limits

**Current:** No rate limiting (development mode)

**Production Recommendation:**
- Implement rate limiting per IP/API key
- Suggested limits:
  - Transcription: 10 requests/minute
  - Translation: 30 requests/minute
  - TTS: 20 requests/minute

---

## CORS Configuration

**Allowed Origins (Development):**
- `http://localhost:8080` (Frontend)
- `http://localhost:8501` (Streamlit)

**Allowed Methods:** All (`*`)

**Allowed Headers:** All (`*`)

**Credentials:** Enabled

**Production Recommendation:** Restrict origins to actual frontend domains.

---

## Configuration

### Environment Variables

Required environment variables (loaded from `.env` file):

```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-...  # Required

# Application Configuration (Optional)
APP_NAME="AI Dubbing Studio API"
DEBUG=false
API_VERSION=v1

# File Upload Configuration (Optional)
MAX_UPLOAD_SIZE=26214400  # 25 MB
TEMP_DIR=/tmp/ai-dubbing-studio

# OpenAI Model Configuration (Optional)
TRANSCRIPTION_MODEL=gpt-4o-transcribe
TRANSLATION_MODEL=gpt-5.1
TTS_MODEL_DEFAULT=tts-1
TTS_VOICE_DEFAULT=onyx

# CORS Configuration (Optional)
CORS_ORIGINS=["http://localhost:8080", "http://localhost:8000"]
CORS_ALLOW_CREDENTIALS=true
```

---

## Technical Architecture

### Technology Stack
- **Framework:** FastAPI 0.115+
- **Python:** 3.13+
- **Audio Processing:** pydub + FFmpeg
- **OpenAI SDK:** AsyncOpenAI (async operations)
- **Validation:** Pydantic 2.x
- **Server:** Uvicorn (ASGI)

### Project Structure
```
backend/
├── api/
│   ├── main.py              # FastAPI app, CORS, exception handlers
│   ├── dependencies.py      # Dependency injection
│   └── routes/
│       ├── health.py        # Health check endpoint
│       └── v1/
│           └── audio.py     # Audio endpoints (v1)
├── core/
│   ├── config.py            # Pydantic BaseSettings
│   ├── exceptions.py        # Custom exceptions
│   └── logging.py           # Structured logging
├── schemas/
│   └── audio.py             # Request/Response Pydantic models
├── services/
│   ├── audio_converter.py   # Audio conversion (pydub)
│   └── openai_client.py     # OpenAI API client
└── utils/
    └── file_handlers.py     # Temp file management
```

### Key Features
- **Async Operations:** All routes use `async def` with AsyncOpenAI
- **Type Safety:** Full type hints, validated with mypy
- **Error Handling:** Custom exceptions with detailed error responses
- **File Management:** Automatic cleanup via BackgroundTasks
- **Logging:** Structured logging with configurable levels
- **Documentation:** Auto-generated OpenAPI/Swagger docs

---

## Running the Backend

### Development
```bash
# Install dependencies
uv sync

# Run server with auto-reload
uv run uvicorn backend.api.main:app --reload --port 8000

# Access API
open http://localhost:8000/docs
```

### Production
```bash
# Run with Gunicorn + Uvicorn workers
gunicorn backend.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## Testing

### Manual Testing (cURL)

**Health Check:**
```bash
curl http://localhost:8000/health
```

**Transcribe Audio:**
```bash
curl -X POST http://localhost:8000/api/v1/audio/transcribe \
  -F "file=@audio.mp3"
```

**Translate Text:**
```bash
curl -X POST http://localhost:8000/api/v1/audio/translate \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello world",
    "source_language": "English",
    "target_language": "Spanish"
  }'
```

**Text-to-Speech:**
```bash
curl -X POST http://localhost:8000/api/v1/audio/tts \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test.",
    "voice": "onyx",
    "model": "tts-1"
  }' \
  --output speech.mp3
```

---

## Integration Notes for Phase 2 (UI) & Phase 3 (Frontend)

### For Streamlit UI (Phase 2)
- Base URL: `http://localhost:8000`
- Use `requests` or `httpx` library
- File upload: Use `files={"file": open(path, "rb")}`
- Binary response: TTS endpoint returns raw MP3 bytes

### For React/Next.js Frontend (Phase 3)
- Use `fetch` or `axios`
- File upload: Use `FormData` for multipart
- CORS already configured for `localhost:8080`
- Binary response: Create blob URL for audio playback

### Example JavaScript Integration
```javascript
// Transcribe audio
const formData = new FormData();
formData.append('file', audioFile);

const response = await fetch('http://localhost:8000/api/v1/audio/transcribe', {
  method: 'POST',
  body: formData,
});

const result = await response.json();
console.log(result.text);

// TTS
const ttsResponse = await fetch('http://localhost:8000/api/v1/audio/tts', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    text: 'Hello world',
    voice: 'onyx',
    model: 'tts-1',
  }),
});

const audioBlob = await ttsResponse.blob();
const audioUrl = URL.createObjectURL(audioBlob);
// Play audio
```

---

## Changelog

### v1 (2025-12-09)
- Initial API release
- Endpoints: health, transcribe, translate, tts
- Async operations with AsyncOpenAI
- Auto-generated OpenAPI documentation
- CORS configuration for local development

---

## Support

For issues or questions, see:
- API Documentation: `http://localhost:8000/docs`
- OpenAPI Spec: `http://localhost:8000/openapi.json`
- Repository: Project root directory
