# AI Dubbing Studio

A web-based application that automates dubbing audio content from one language to another using OpenAI's AI models for transcription, translation, and text-to-speech generation.

## Features

- **Audio Upload** - Support for OGG, MP3, WAV, and M4A formats
- **Automatic Transcription** - Converts audio to text using OpenAI's GPT-4O transcription model
- **Manual Editing** - Review and correct transcription errors before translation
- **Language Translation** - Translates text between any language pair using GPT-5.1
- **Text-to-Speech** - Generates natural-sounding audio using OpenAI TTS
- **Voice Selection** - 6 voices available: alloy, echo, fable, onyx, nova, shimmer
- **Quality Options** - Choose between `tts-1` (faster) or `tts-1-hd` (higher quality)
- **Audio Download** - Export the final dubbed audio as MP3

## Workflow

1. **Upload & Transcribe** - Upload audio file, automatically transcribed to text
2. **Edit & Translate** - Review/edit transcription, then translate and generate speech
3. **Download** - Listen to result and download the dubbed MP3

## Prerequisites

- Python 3.13+
- FFmpeg (system dependency)
- OpenAI API key

### Installing FFmpeg

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows - download from https://ffmpeg.org/download.html
```

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd ai-dubbing-studio-app

# Install dependencies with uv
uv sync

# Or with pip
pip install -e .
```

## Usage

```bash
# Run the application
uv run streamlit run app.py
```

The application opens at `http://localhost:8501`. Enter your OpenAI API key in the sidebar to get started.

## Dependencies

| Package | Purpose |
|---------|---------|
| streamlit | Web UI framework |
| openai | OpenAI API client |
| pydub | Audio format conversion |
| audioop-lts | Audio operations (Python 3.13 compatibility) |

## License

MIT
