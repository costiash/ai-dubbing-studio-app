"""Pydantic schemas for audio-related endpoints."""

from pydantic import BaseModel, Field


class TranscribeResponse(BaseModel):
    """Response schema for audio transcription."""

    text: str = Field(
        ...,
        description="Transcribed text from audio",
        min_length=1,
    )
    language: str | None = Field(
        default=None,
        description="Detected or specified language",
    )


class TranslateRequest(BaseModel):
    """Request schema for text translation."""

    text: str = Field(
        ...,
        description="Text to translate",
        min_length=1,
        max_length=50000,
    )
    source_language: str = Field(
        ...,
        description="Source language (e.g., 'Hebrew', 'English')",
        min_length=1,
        max_length=50,
    )
    target_language: str = Field(
        ...,
        description="Target language (e.g., 'Russian', 'Spanish')",
        min_length=1,
        max_length=50,
    )


class TranslateResponse(BaseModel):
    """Response schema for text translation."""

    translated_text: str = Field(
        ...,
        description="Translated text",
        min_length=1,
    )
    source_language: str = Field(
        ...,
        description="Source language",
    )
    target_language: str = Field(
        ...,
        description="Target language",
    )


class TTSRequest(BaseModel):
    """Request schema for text-to-speech generation.

    The gpt-4o-mini-tts model supports an 'instructions' parameter for controlling
    voice characteristics like accent, emotional range, intonation, speed, and tone.
    """

    text: str = Field(
        ...,
        description="Text to convert to speech",
        min_length=1,
        max_length=4096,
    )
    voice: str = Field(
        default="onyx",
        description=(
            "Voice to use. Available voices for gpt-4o-mini-tts: "
            "alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer"
        ),
    )
    model: str = Field(
        default="gpt-4o-mini-tts",
        description=(
            "TTS model: gpt-4o-mini-tts (supports instructions), "
            "tts-1 (fast), or tts-1-hd (high quality)"
        ),
    )
    instructions: str | None = Field(
        default=None,
        description=(
            "Voice style instructions for gpt-4o-mini-tts. "
            "Example: 'Speak in a warm, friendly tone with moderate pacing.' "
            "Can control accent, emotional range, intonation, speed, tone, whispering."
        ),
        max_length=1000,
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, this is a test of text-to-speech.",
                "voice": "onyx",
                "model": "gpt-4o-mini-tts",
                "instructions": "Speak in a clear, professional tone with moderate pacing.",
            }
        }


class HealthResponse(BaseModel):
    """Response schema for health check endpoint."""

    status: str = Field(
        default="healthy",
        description="Health status",
    )
    openai_api_configured: bool = Field(
        ...,
        description="Whether OpenAI API key is configured",
    )
    version: str = Field(
        ...,
        description="API version",
    )


class ErrorResponse(BaseModel):
    """Response schema for errors."""

    detail: str = Field(
        ...,
        description="Error message",
    )
    error_code: str | None = Field(
        default=None,
        description="Machine-readable error code",
    )
    errors: dict[str, list[str]] | None = Field(
        default=None,
        description="Validation errors",
    )
