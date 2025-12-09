"""Audio processing endpoints (v1)."""

from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response

from backend.core.exceptions import (
    AudioProcessingError,
    FileValidationError,
    TranscriptionError,
    TranslationError,
    TTSError,
)
from backend.core.logging import get_logger
from backend.schemas.audio import (
    TranscribeResponse,
    TranslateRequest,
    TranslateResponse,
    TTSRequest,
)
from backend.services.audio_converter import convert_to_mp3
from backend.services.openai_client import OpenAIService, get_openai_service
from backend.utils.file_handlers import (
    cleanup_files,
    get_temp_file_path,
    save_upload_file,
    validate_audio_file,
)

logger = get_logger(__name__)
router = APIRouter(prefix="/audio", tags=["audio"])


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    summary="Transcribe Audio",
    description="Upload an audio file and receive transcribed text",
    status_code=200,
)
async def transcribe_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(..., description="Audio file (OGG, MP3, WAV, M4A)"),
    openai_service: OpenAIService = Depends(get_openai_service),
) -> TranscribeResponse:
    """Transcribe audio file to text.

    Args:
        background_tasks: FastAPI background tasks for cleanup
        file: Uploaded audio file
        openai_service: OpenAI service dependency

    Returns:
        Transcribed text and detected language

    Raises:
        HTTPException: If transcription fails
    """
    temp_input: Path | None = None
    temp_mp3: Path | None = None

    try:
        # Validate file
        validate_audio_file(file)

        # Save uploaded file
        file_ext = Path(file.filename or "audio.tmp").suffix
        temp_input = get_temp_file_path(suffix=file_ext)
        await save_upload_file(file, temp_input)

        # Convert to MP3
        temp_mp3 = get_temp_file_path(suffix=".mp3")
        await convert_to_mp3(temp_input, temp_mp3)

        # Transcribe
        with open(temp_mp3, "rb") as audio_file:
            text, language = await openai_service.transcribe_audio(audio_file)

        # Schedule cleanup
        background_tasks.add_task(cleanup_files, temp_input, temp_mp3)

        return TranscribeResponse(text=text, language=language)

    except FileValidationError as e:
        logger.error(f"File validation failed: {e}")
        if temp_input:
            background_tasks.add_task(cleanup_files, temp_input)
        raise HTTPException(status_code=400, detail=str(e)) from e

    except AudioProcessingError as e:
        logger.error(f"Audio processing failed: {e}")
        if temp_input or temp_mp3:
            files_to_clean = [f for f in [temp_input, temp_mp3] if f is not None]
            if files_to_clean:
                background_tasks.add_task(cleanup_files, *files_to_clean)
        raise HTTPException(status_code=500, detail=str(e)) from e

    except TranscriptionError as e:
        logger.error(f"Transcription failed: {e}")
        if temp_input or temp_mp3:
            files_to_clean = [f for f in [temp_input, temp_mp3] if f is not None]
            if files_to_clean:
                background_tasks.add_task(cleanup_files, *files_to_clean)
        raise HTTPException(status_code=500, detail=str(e)) from e

    except Exception as e:
        logger.error(f"Unexpected error during transcription: {e}")
        if temp_input or temp_mp3:
            files_to_clean = [f for f in [temp_input, temp_mp3] if f is not None]
            if files_to_clean:
                background_tasks.add_task(cleanup_files, *files_to_clean)
        raise HTTPException(status_code=500, detail=f"Transcription failed: {e}") from e


@router.post(
    "/translate",
    response_model=TranslateResponse,
    summary="Translate Text",
    description="Translate text from one language to another",
    status_code=200,
)
async def translate_text(
    request: TranslateRequest,
    openai_service: OpenAIService = Depends(get_openai_service),
) -> TranslateResponse:
    """Translate text from source to target language.

    Args:
        request: Translation request with text and languages
        openai_service: OpenAI service dependency

    Returns:
        Translated text

    Raises:
        HTTPException: If translation fails
    """
    try:
        translated_text = await openai_service.translate_text(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language,
        )

        return TranslateResponse(
            translated_text=translated_text,
            source_language=request.source_language,
            target_language=request.target_language,
        )

    except TranslationError as e:
        logger.error(f"Translation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

    except Exception as e:
        logger.error(f"Unexpected error during translation: {e}")
        raise HTTPException(status_code=500, detail=f"Translation failed: {e}") from e


@router.post(
    "/tts",
    summary="Text-to-Speech",
    description="Convert text to speech audio (MP3)",
    status_code=200,
    response_class=Response,
    responses={
        200: {
            "content": {"audio/mpeg": {}},
            "description": "Generated audio file (MP3)",
        }
    },
)
async def text_to_speech(
    request: TTSRequest,
    openai_service: OpenAIService = Depends(get_openai_service),
) -> Response:
    """Convert text to speech.

    Args:
        request: TTS request with text, voice, and model
        openai_service: OpenAI service dependency

    Returns:
        Audio file as MP3

    Raises:
        HTTPException: If TTS generation fails
    """
    try:
        audio_bytes = await openai_service.generate_speech(
            text=request.text,
            voice=request.voice,
            model=request.model,
        )

        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Disposition": "attachment; filename=speech.mp3",
            },
        )

    except TTSError as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e

    except Exception as e:
        logger.error(f"Unexpected error during TTS generation: {e}")
        raise HTTPException(status_code=500, detail=f"TTS generation failed: {e}") from e
