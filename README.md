# AI Dubbing Studio

A web application that automates audio dubbing between languages using OpenAI's AI models for transcription, translation, and text-to-speech.

## Quick Start

### Prerequisites

- **Python 3.13+**
- **Node.js 18+** (for frontend dev server)
- **FFmpeg** (audio processing)
- **OpenAI API key**

```bash
# Install FFmpeg
sudo apt install ffmpeg      # Ubuntu/Debian
brew install ffmpeg          # macOS
```

### Setup

```bash
# Clone and enter directory
git clone <repository-url>
cd ai-dubbing-studio-app

# Install Python dependencies
uv sync

# Create environment file
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# Start both servers
./start.sh
```

Open **http://localhost:8080** in your browser.

### Manual Start (Alternative)

```bash
# Terminal 1: Backend (FastAPI)
uv run uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2: Frontend (Python HTTP server)
cd frontend && python server.py
```

## Features

| Feature | Description |
|---------|-------------|
| **Audio Upload** | Drag-and-drop support for OGG, MP3, WAV, M4A (max 25MB) |
| **Transcription** | Automatic speech-to-text using GPT-4O |
| **Translation** | Any language pair via GPT-5.1 |
| **Text-to-Speech** | 6 voices, standard or HD quality |
| **Session Persistence** | Resume work after page refresh |
| **Dark/Light Mode** | System-aware theme switching |

## How It Works

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. Upload   │ → │ 2. Edit &    │ → │ 3. Download  │
│  & Transcribe│    │    Translate │    │    Audio     │
└──────────────┘    └──────────────┘    └──────────────┘
```

1. **Upload** an audio file → automatically transcribed to text
2. **Review** the transcription, select target language, generate dubbed audio
3. **Download** the final MP3

## Architecture

```
Frontend (localhost:8080)          Backend (localhost:8000)
┌────────────────────┐             ┌────────────────────┐
│  Vanilla JavaScript │ ─── REST ─→│  FastAPI + Python  │
│  ES6 Modules        │             │  Pydantic schemas  │
│  Manager Pattern    │             │  Async/await       │
└────────────────────┘             └─────────┬──────────┘
                                             │
                                    ┌────────▼────────┐
                                    │   OpenAI API    │
                                    │  GPT-4O, GPT-5.1│
                                    │  TTS-1/TTS-1-HD │
                                    └─────────────────┘
```

## Development

### Backend Commands

```bash
uv run pytest backend/tests/              # Run tests
uv run pytest backend/tests/ --cov        # With coverage
uv run ruff check backend/ --fix          # Lint & fix
uv run ruff format backend/               # Format
uv run mypy backend/                      # Type check
```

### Frontend Commands

```bash
cd frontend
npm test                                  # Run Vitest tests
npm run test:coverage                     # With coverage
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/api/v1/audio/transcribe` | Upload audio → text |
| `POST` | `/api/v1/audio/translate` | Text → translated text |
| `POST` | `/api/v1/audio/tts` | Text → speech (MP3) |

## Project Structure

```
ai-dubbing-studio-app/
├── backend/                 # FastAPI server
│   ├── api/routes/         # API endpoints
│   ├── services/           # OpenAI client, audio converter
│   ├── schemas/            # Pydantic models
│   └── tests/              # pytest suite (114 tests)
├── frontend/               # JavaScript SPA
│   ├── scripts/managers/   # UI state, file upload, audio processing
│   ├── scripts/services/   # Health check service
│   └── tests/              # Vitest suite
├── docs/                   # Documentation
├── design/                 # Design system & tokens
└── start.sh               # Development startup script
```

## Documentation

| Document | Description |
|----------|-------------|
| [API Reference](docs/API.md) | REST API endpoints, schemas, error codes |
| [Architecture](docs/ARCHITECTURE.md) | System design and data flow |
| [Testing Guide](docs/TESTING.md) | Backend testing with pytest |
| [Deployment](docs/DEPLOYMENT.md) | Production deployment |
| [AI Docs](ai_docs/) | OpenAI API reference |

## Tech Stack

- **Backend:** FastAPI, Pydantic, uvicorn, pydub
- **Frontend:** Vanilla JavaScript (ES6), HTML5, CSS3
- **AI:** OpenAI API (GPT-4O, GPT-5.1, TTS)
- **Tools:** uv (packages), pytest, Vitest, Ruff, mypy

## License

MIT
