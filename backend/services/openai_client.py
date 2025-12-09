"""OpenAI client service for transcription, translation, and TTS."""

from typing import BinaryIO

from openai import AsyncOpenAI

from backend.core.config import settings
from backend.core.exceptions import TranscriptionError, TranslationError, TTSError
from backend.core.logging import get_logger

logger = get_logger(__name__)


class OpenAIService:
    """Service for interacting with OpenAI API."""

    def __init__(self, api_key: str | None = None) -> None:
        """Initialize OpenAI service.

        Args:
            api_key: OpenAI API key (defaults to settings.openai_api_key)
        """
        self.api_key = api_key or settings.openai_api_key
        self.client = AsyncOpenAI(api_key=self.api_key)
        logger.info("Initialized OpenAI service")

    async def transcribe_audio(
        self,
        audio_file: BinaryIO,
        language: str | None = None,
    ) -> tuple[str, str | None]:
        """Transcribe audio file to text.

        Args:
            audio_file: Audio file object (opened in binary mode)
            language: Optional language hint

        Returns:
            Tuple of (transcribed_text, detected_language)

        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            logger.info(f"Transcribing audio with model {settings.transcription_model}")

            response = await self.client.audio.transcriptions.create(  # type: ignore[call-overload]
                model=settings.transcription_model,
                file=audio_file,
                response_format="json",
                language=language,
            )

            # Handle response safely (support both object and dict responses)
            text = response.text if hasattr(response, "text") else response["text"]
            detected_lang = (
                response.language if hasattr(response, "language") else response.get("language")
            )

            logger.info(f"Transcription successful, detected language: {detected_lang}")
            return text, detected_lang

        except Exception as e:
            error_msg = f"Transcription failed: {e}"
            logger.error(error_msg)
            raise TranscriptionError(error_msg, details={"error": str(e)}) from e

    async def translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        """Translate text from source to target language.

        Args:
            text: Text to translate
            source_language: Source language name
            target_language: Target language name

        Returns:
            Translated text

        Raises:
            TranslationError: If translation fails
        """
        try:
            logger.info(
                f"Translating from {source_language} to {target_language} "
                f"using {settings.translation_model}"
            )

            response = await self.client.chat.completions.create(
                model=settings.translation_model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"Translate the following text from {source_language} "
                            f"to {target_language}. Provide a natural, fluent translation. "
                            f"Return ONLY the translated text, no explanations."
                        ),
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                temperature=0.3,  # Lower temperature for more consistent translations
            )

            translated_text = response.choices[0].message.content
            if not translated_text:
                raise TranslationError("Translation returned empty response")

            logger.info("Translation successful")
            return translated_text

        except Exception as e:
            error_msg = f"Translation failed: {e}"
            logger.error(error_msg)
            raise TranslationError(error_msg, details={"error": str(e)}) from e

    async def generate_speech(
        self,
        text: str,
        voice: str = "onyx",
        model: str = "tts-1",
    ) -> bytes:
        """Generate speech from text using TTS.

        Args:
            text: Text to convert to speech
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            model: TTS model (tts-1 or tts-1-hd)

        Returns:
            Audio data as bytes (MP3 format)

        Raises:
            TTSError: If TTS generation fails
        """
        try:
            logger.info(f"Generating speech with model {model}, voice {voice}")

            response = await self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text,
            )

            # Read response content into bytes
            audio_bytes = response.read()

            logger.info(f"Generated {len(audio_bytes)} bytes of audio")
            return audio_bytes

        except Exception as e:
            error_msg = f"TTS generation failed: {e}"
            logger.error(error_msg)
            raise TTSError(error_msg, details={"error": str(e)}) from e

    async def close(self) -> None:
        """Close the OpenAI client and cleanup resources.

        Should be called during application shutdown to properly close HTTP connections.
        """
        try:
            await self.client.close()
            logger.info("Closed OpenAI client")
        except Exception as e:
            logger.warning(f"Error closing OpenAI client: {e}")


# Global service instance
_openai_service: OpenAIService | None = None


def get_openai_service() -> OpenAIService:
    """Get or create OpenAI service instance (dependency injection).

    Returns:
        OpenAI service instance
    """
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
