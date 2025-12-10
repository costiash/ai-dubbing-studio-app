"""Application configuration using Pydantic BaseSettings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # OpenAI Configuration
    openai_api_key: str = Field(
        ...,
        description="OpenAI API key for authentication",
    )

    # Application Configuration
    app_name: str = Field(
        default="AI Dubbing Studio API",
        description="Application name",
    )
    debug: bool = Field(
        default=False,
        description="Enable debug mode",
    )
    api_version: str = Field(
        default="v1",
        description="API version",
    )

    # File Upload Configuration
    max_upload_size: int = Field(
        default=26214400,  # 25 MB (OpenAI limit)
        description="Maximum file upload size in bytes",
    )
    allowed_audio_formats: list[str] = Field(
        default=["audio/mpeg", "audio/ogg", "audio/wav", "audio/x-m4a", "audio/mp4"],
        description="Allowed audio MIME types",
    )
    temp_dir: str = Field(
        default="/tmp/ai-dubbing-studio",
        description="Directory for temporary files",
    )

    # OpenAI Model Configuration
    transcription_model: str = Field(
        default="gpt-4o-transcribe",
        description="OpenAI model for audio transcription (gpt-4o-transcribe, gpt-4o-mini-transcribe, whisper-1)",
    )
    translation_model: str = Field(
        default="gpt-5.1",
        description="OpenAI model for text translation",
    )
    translation_temperature: float = Field(
        default=0.3,
        description="Temperature for translation (lower = more consistent)",
    )
    tts_model_default: str = Field(
        default="gpt-4o-mini-tts",
        description="Default OpenAI TTS model (gpt-4o-mini-tts for instructions support, tts-1, tts-1-hd)",
    )
    tts_voice_default: str = Field(
        default="onyx",
        description="Default TTS voice",
    )
    # Available TTS voices: alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer
    tts_available_voices: list[str] = Field(
        default=["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"],
        description="Available TTS voices for gpt-4o-mini-tts",
    )

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080", "http://localhost:8501"],
        description="Allowed CORS origins",
    )
    cors_allow_credentials: bool = Field(
        default=True,
        description="Allow credentials in CORS requests",
    )


# Global settings instance
# Note: This will load from .env file or environment variables
settings = Settings()  # type: ignore[call-arg]


def get_settings() -> Settings:
    """Dependency function for FastAPI to inject settings.

    This allows tests to override settings using dependency_overrides.

    Returns:
        Settings instance
    """
    return settings
