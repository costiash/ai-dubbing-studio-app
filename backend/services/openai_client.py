"""OpenAI client service for transcription, translation, and TTS.

This module implements OpenAI API integration with prompt engineering best practices
based on official OpenAI documentation and GPT-5.1 prompting guidelines.

Key features:
- Transcription with contextual prompts for improved accuracy
- Translation with structured GPT-5.1 optimized prompts
- TTS with gpt-4o-mini-tts instructions for voice control
"""

from typing import BinaryIO

from openai import AsyncOpenAI

from backend.core.config import settings
from backend.core.exceptions import TranscriptionError, TranslationError, TTSError
from backend.core.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# GPT-5.1 Optimized Translation Prompts
# =============================================================================
# Based on OpenAI Cookbook GPT-5.1 Prompting Guide best practices:
# - Structured prompts with XML-like tags for clear boundaries
# - Explicit output formatting instructions
# - Lower temperature (0.3) for consistent translations
# - Clear role definition and task constraints

TRANSLATION_SYSTEM_PROMPT = """You are an expert translator. Translate the user's text from {source_language} to {target_language}.

Requirements:
- Produce ONLY the translated text with no additional commentary, explanation, or meta-text
- Ensure the translation sounds natural and native to speakers of {target_language}
- Preserve the original tone (formal/informal, emotional/neutral)
- Adapt idioms and cultural references appropriately while maintaining meaning
- Keep technical terms, proper nouns, and brand names unchanged as appropriate

Critical: Output ONLY the translation itself. Do not include:
- Checklists or bullet points about your approach
- Introductory phrases like "Here is the translation:"
- Validation or self-assessment of your translation
- Any text that is not part of the direct translation"""


# =============================================================================
# TTS Voice Instructions
# =============================================================================
# Based on OpenAI TTS documentation for gpt-4o-mini-tts:
# - Instructions can control: accent, emotional range, intonation, speed, tone
# - Natural language prompts for voice style

DEFAULT_TTS_INSTRUCTIONS = """Speak in a clear, natural, and professional tone.
Maintain a moderate pace that is easy to follow.
Use appropriate intonation and emphasis to convey meaning clearly."""

TTS_INSTRUCTIONS_BY_CONTEXT = {
    "narration": "Speak in a warm, engaging narrator voice with good pacing and clear enunciation.",
    "conversation": "Speak naturally as in casual conversation, with varied intonation and relaxed pacing.",
    "professional": "Speak in a clear, authoritative, and professional tone suitable for business content.",
    "emotional": "Speak with appropriate emotional expression, varying tone to match the content's sentiment.",
}


# =============================================================================
# Transcription Refinement Prompt
# =============================================================================
# GPT-5.1 prompt for linguistic and contextual refinement of transcriptions.
# This is a lightweight post-processing step that improves accuracy without
# requiring re-transcription of the audio.

TRANSCRIPTION_REFINEMENT_PROMPT = """You are a professional transcription editor and linguist specializing in {language}.

Your task is to refine a raw speech-to-text transcription for linguistic accuracy, grammar, and contextual correctness.

<input_transcription>
{transcription}
</input_transcription>

Review and correct:
1. **Phonetic misrecognitions**: Fix words that sound similar but are contextually wrong
2. **Grammar and syntax**: Ensure proper sentence structure for {language}
3. **Punctuation**: Add or correct punctuation for natural reading flow
4. **Contextual coherence**: Ensure the text makes logical sense
5. **Filler words**: Keep natural speech patterns but remove obvious recognition errors

Guidelines:
- Preserve the original meaning and speaker intent
- Maintain the speaking style (formal/informal)
- Do NOT translate - keep everything in the original {language}
- Do NOT add content that wasn't spoken
- Do NOT remove meaningful words

Output ONLY the refined transcription text. No explanations, no meta-commentary."""


# Language code to name mapping for prompt generation
LANGUAGE_CODE_TO_NAME = {
    "en": "English",
    "he": "Hebrew",
    "ru": "Russian",
    "es": "Spanish",
    "ar": "Arabic",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "hi": "Hindi",
    "pl": "Polish",
    "uk": "Ukrainian",
    "tr": "Turkish",
    "nl": "Dutch",
    "sv": "Swedish",
}


class OpenAIService:
    """Service for interacting with OpenAI API.

    Implements best practices from OpenAI documentation:
    - Transcription: Uses prompt parameter for context and vocabulary hints
    - Translation: Uses GPT-5.1 optimized structured prompts
    - TTS: Supports gpt-4o-mini-tts with instructions for voice control
    """

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
        prompt: str | None = None,
        model: str | None = None,
    ) -> tuple[str, str | None]:
        """Transcribe audio file to text.

        Uses the prompt parameter to improve transcription quality. Based on OpenAI docs,
        the prompt can help with:
        - Correcting specific words or acronyms the model may misrecognize
        - Providing context about the audio content
        - Preserving punctuation style
        - Keeping filler words in the transcript

        Args:
            audio_file: Audio file object (opened in binary mode)
            language: Optional language hint (ISO 639-1 code)
            prompt: Optional context prompt to improve transcription accuracy.
                    Example: "The following is a conversation about AI and machine learning.
                    Technical terms include GPT, transformer, embeddings."
            model: Optional model override. Options:
                   - "whisper-1" (for auto-detection flow)
                   - "gpt-4o-mini-transcribe" (fast, for user-specified language)
                   - "gpt-4o-transcribe" (high quality, for refined transcription)

        Returns:
            Tuple of (transcribed_text, detected_language)

        Raises:
            TranscriptionError: If transcription fails
        """
        try:
            # Use specified model or default from settings
            transcription_model = model or settings.transcription_model
            logger.info(f"Transcribing audio with model {transcription_model}")
            if prompt:
                logger.info(f"Using transcription prompt: {prompt[:100]}...")

            # Build request parameters
            request_params: dict = {
                "model": transcription_model,
                "file": audio_file,
                "response_format": "json",
            }

            # Add optional parameters if provided
            if language:
                request_params["language"] = language
            # Prompt is only supported by gpt-4o-transcribe and gpt-4o-mini-transcribe
            if prompt and transcription_model in ("gpt-4o-transcribe", "gpt-4o-mini-transcribe"):
                request_params["prompt"] = prompt

            response = await self.client.audio.transcriptions.create(**request_params)

            # OpenAI returns Pydantic models - use getattr for safe attribute access
            text = response.text
            detected_lang = getattr(response, "language", None)

            logger.info(f"Transcription successful, detected language: {detected_lang}")
            return text, detected_lang

        except Exception as e:
            error_msg = f"Transcription failed: {e}"
            logger.error(error_msg)
            raise TranscriptionError(error_msg, details={"error": str(e)}) from e

    async def refine_transcription(
        self,
        transcription: str,
        language: str,
    ) -> str:
        """Refine a raw transcription using GPT-5.1 for linguistic accuracy.

        This lightweight post-processing step improves transcription quality by:
        - Fixing phonetic misrecognitions (words that sound similar)
        - Correcting grammar and syntax
        - Adding proper punctuation
        - Ensuring contextual coherence

        Args:
            transcription: Raw transcription text from speech-to-text model
            language: Language name (e.g., "Hebrew", "English") or code (e.g., "he", "en")

        Returns:
            Refined transcription text

        Note:
            If refinement fails, returns the original transcription unchanged.
        """
        try:
            # Convert language code to name if needed
            language_name = LANGUAGE_CODE_TO_NAME.get(language.lower(), language.title())

            logger.info(f"Refining transcription ({len(transcription)} chars) for {language_name}")

            # Format the prompt with language and transcription
            prompt = TRANSCRIPTION_REFINEMENT_PROMPT.format(
                language=language_name,
                transcription=transcription,
            )

            # GPT-5.1 with no reasoning (allows temperature control for consistency)
            response = await self.client.chat.completions.create(
                model=settings.translation_model,  # Uses gpt-5.1
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],
                reasoning_effort="none",  # Required to use temperature parameter
                temperature=0.2,  # Low temperature for consistent output
            )

            refined_text = response.choices[0].message.content
            if not refined_text:
                logger.warning("Refinement returned empty, using original transcription")
                return transcription

            logger.info(
                f"Transcription refined: {len(transcription)} → {len(refined_text)} chars"
            )
            return refined_text.strip()

        except Exception as e:
            # Non-fatal: return original transcription if refinement fails
            logger.warning(f"Transcription refinement failed: {e}, using original")
            return transcription

    async def translate_text(
        self,
        text: str,
        source_language: str,
        target_language: str,
    ) -> str:
        """Translate text from source to target language.

        Uses GPT-5.1 optimized prompting with:
        - Structured system prompt with XML-like tags
        - Lower temperature (0.3) for consistent translations
        - Clear output constraints to prevent explanatory text

        Args:
            text: Text to translate
            source_language: Source language name (e.g., "Hebrew", "English")
            target_language: Target language name (e.g., "Russian", "Spanish")

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

            # Format the structured system prompt with language parameters
            system_prompt = TRANSLATION_SYSTEM_PROMPT.format(
                source_language=source_language,
                target_language=target_language,
            )

            # GPT-5.1 requires reasoning_effort="none" to use temperature parameter
            response = await self.client.chat.completions.create(
                model=settings.translation_model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": text,
                    },
                ],
                reasoning_effort="none",  # Required for temperature support
                temperature=settings.translation_temperature,  # Lower for consistency
            )

            translated_text = response.choices[0].message.content
            if not translated_text:
                raise TranslationError("Translation returned empty response")

            logger.info("Translation successful")
            return translated_text.strip()

        except Exception as e:
            error_msg = f"Translation failed: {e}"
            logger.error(error_msg)
            raise TranslationError(error_msg, details={"error": str(e)}) from e

    async def generate_speech(
        self,
        text: str,
        voice: str = "onyx",
        model: str | None = None,
        instructions: str | None = None,
    ) -> bytes:
        """Generate speech from text using TTS.

        Supports the new gpt-4o-mini-tts model with instructions parameter for
        controlling voice characteristics like:
        - Accent
        - Emotional range
        - Intonation
        - Speed of speech
        - Tone
        - Whispering

        Args:
            text: Text to convert to speech
            voice: Voice to use. Available voices for gpt-4o-mini-tts:
                   alloy, ash, ballad, coral, echo, fable, nova, onyx, sage, shimmer
            model: TTS model. Options:
                   - "gpt-4o-mini-tts" (default, supports instructions)
                   - "tts-1" (fast, lower quality)
                   - "tts-1-hd" (high quality, no instructions support)
            instructions: Voice style instructions for gpt-4o-mini-tts.
                         Example: "Speak in a warm, friendly tone with moderate pacing."
                         Only works with gpt-4o-mini-tts model.

        Returns:
            Audio data as bytes (MP3 format)

        Raises:
            TTSError: If TTS generation fails
        """
        try:
            # Use configured default model if not specified
            model = model or settings.tts_model_default
            logger.info(f"Generating speech with model {model}, voice {voice}")

            # Build request parameters
            request_params: dict = {
                "model": model,
                "voice": voice,
                "input": text,
            }

            # Add instructions only for gpt-4o-mini-tts (other models don't support it)
            if model == "gpt-4o-mini-tts":
                # Use provided instructions or default
                tts_instructions = instructions or DEFAULT_TTS_INSTRUCTIONS
                request_params["instructions"] = tts_instructions
                logger.info(f"Using TTS instructions: {tts_instructions[:80]}...")

            response = await self.client.audio.speech.create(**request_params)

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
