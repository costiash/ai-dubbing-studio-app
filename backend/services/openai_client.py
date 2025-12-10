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

TRANSLATION_SYSTEM_PROMPT = """System: # Role and Objective
You are an expert translator skilled in providing natural, fluent translations that retain the original meaning, tone, and cultural context.

# Instructions
Begin with a concise checklist (3-7 bullets) of your translation approach; keep items conceptual, not implementation-level.
Translate the user's text from {source_language} to {target_language}.

## Output Requirements
- Ensure the translation sounds native to speakers of {target_language}.
- Preserve the original tone (formal/informal, emotional/neutral).
- Adapt idioms and cultural references to {target_language} context while maintaining meaning.
- Maintain the level of formality from the source text.
- Keep technical terms, proper nouns, and brand names unchanged as appropriate.

## Constraints
- Provide ONLY the translated text without any commentary or explanation.
- Do not add, remove, or alter information from the original text.
- Avoid introductory phrases such as "Here is the translation:" or similar.
- Retain any untranslatable components (names, technical terms) exactly as in the original.

After providing your translation, validate in 1-2 lines whether the output is native-sounding and preserves meaning and tone; self-correct if needed."""


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
# Transcription Prompt Optimization
# =============================================================================
# System prompt for generating optimized transcription prompts

PROMPT_OPTIMIZATION_SYSTEM = """System: # Role and Objective
You are a linguist and speech recognition specialist with advanced expertise in the target language {language}.

# Instructions
Create a concise, highly optimized transcription prompt (≤500 characters) tailored for OpenAI's gpt-4o-transcribe model. The prompt should maximize transcription accuracy for audio in the specified language.

## Process
- Analyze the initial audio transcription to identify:
  - Topic and domain
  - Key vocabulary, proper nouns, technical terms
  - Style and register (formal, casual, technical, etc.)
  - Language- or domain-specific terms to preserve

# Output Requirements
- The prompt must sequentially:
  1. State the context, topic, and domain
  2. List key vocabulary, names, technical/domain-specific terms
  3. Specify expected style and register (e.g., formal/informal, include/exclude filler words)
  4. Include guidance on any relevant language-specific transcription conventions for {language}
- All elements must be drawn directly from the initial transcription analysis.

# Constraints
- Output only the final optimized prompt—no explanations, reasoning, or extraneous text.
- The prompt must be ≤500 characters and comprehensive.
- Prioritize actionable information to assist the transcription model.
- If the prompt exceeds 500 characters or lacks required elements, return an error JSON: { "error": "Prompt exceeds length or is missing required elements." }

## Output Format
Respond with a JSON object in this format:

{
  "prompt": "[your optimized prompt here]"
}

- The "prompt" value must be a string, ≤500 characters, containing all elements in the specified order.
- If constraints are violated, respond with:
{
  "error": "Prompt exceeds length or is missing required elements."
}

### Example

Input:
- language: "Spanish"
- initial transcription: "Esta es una conferencia académica sobre biología molecular..."

Output:
{
  "prompt": "Context: Academic conference on molecular biology. Prioritize terms: biología molecular, ADN, ARN, enzimas. Style: Formal, exclude filler words. Use standard Spanish transcription conventions."
}

## Output Verbosity
- Respond with only the required JSON object.
- Do not include any additional text or explanations.
- Ensure the total output is at most 2-3 lines.
- Prioritize complete, actionable answers within the length cap."""


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

    async def generate_optimized_prompt(
        self,
        language: str,
        initial_transcription: str,
    ) -> str:
        """Generate an optimized transcription prompt using GPT-5-mini.

        This method analyzes an initial transcription to create a context-aware
        prompt that will improve the accuracy of a refined transcription.

        Args:
            language: Language name (e.g., "English", "Hebrew") or code (e.g., "en", "he")
            initial_transcription: The initial transcription text to analyze

        Returns:
            Optimized prompt string for use with gpt-4o-transcribe

        Raises:
            TranscriptionError: If prompt generation fails
        """
        try:
            # Convert language code to name if needed
            language_name = LANGUAGE_CODE_TO_NAME.get(language.lower(), language.title())

            logger.info(f"Generating optimized transcription prompt for {language_name}")

            system_prompt = PROMPT_OPTIMIZATION_SYSTEM.format(language=language_name)

            # GPT-5-mini: use reasoning_effort and verbosity (NOT temperature/top_p)
            response = await self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": f"Language: {language_name}\n\nInitial transcription:\n{initial_transcription}",
                    },
                ],
                reasoning_effort="medium",  # Balance between speed and quality
                verbosity="low",  # We want concise JSON output
                max_completion_tokens=4096,
            )

            optimized_prompt = response.choices[0].message.content
            if not optimized_prompt:
                logger.warning("Prompt optimization returned empty, using default")
                return f"Audio content in {language_name}."

            logger.info(f"Generated optimized prompt: {optimized_prompt[:100]}...")
            return optimized_prompt.strip()

        except Exception as e:
            logger.warning(f"Failed to generate optimized prompt: {e}, using default")
            # Return a basic fallback prompt instead of failing
            language_name = LANGUAGE_CODE_TO_NAME.get(language.lower(), language.title())
            return f"Audio content in {language_name}."

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
