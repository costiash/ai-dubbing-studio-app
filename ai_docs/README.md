# AI Documentation Reference

This directory contains reference documentation for AI services used by the AI Dubbing Studio.

## OpenAI API Reference

| Document | Description |
|----------|-------------|
| [audio-openai-api-reference.md](audio-openai-api-reference.md) | Complete Audio API reference |
| [speech-to-text-openai-api.md](speech-to-text-openai-api.md) | Transcription API (Whisper/GPT-4O) |
| [text-to-speech-openai-api.md](text-to-speech-openai-api.md) | TTS API (tts-1, tts-1-hd) |
| [using-gpt-5-1-openai-api.md](using-gpt-5-1-openai-api.md) | GPT-5.1 for translation |

## Usage

These docs are reference material for understanding the OpenAI APIs used in this project:

- **Transcription**: `gpt-4o-transcribe` model
- **Translation**: `gpt-5.1` model
- **Text-to-Speech**: `tts-1` or `tts-1-hd` models

For implementation details, see `backend/services/openai_client.py`.
