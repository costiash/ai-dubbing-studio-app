"""FastAPI application entry point."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.routes import health
from backend.api.routes.v1 import audio
from backend.core.config import settings
from backend.core.exceptions import (
    AudioProcessingError,
    FileValidationError,
    TranscriptionError,
    TranslationError,
    TTSError,
)
from backend.core.logging import get_logger, setup_logging
from backend.services.openai_client import get_openai_service
from backend.utils.file_handlers import ensure_temp_dir

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan manager.

    Handles startup and shutdown tasks.

    Args:
        app: FastAPI application instance

    Yields:
        None during application runtime
    """
    # Startup
    setup_logging()
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Debug mode: {settings.debug}")

    # Ensure temp directory exists
    ensure_temp_dir()
    logger.info(f"Temporary directory: {settings.temp_dir}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.app_name}")

    # Close OpenAI client to cleanup HTTP connections
    try:
        service = get_openai_service()
        await service.close()
    except Exception as e:
        logger.warning(f"Error during OpenAI client shutdown: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description="AI-powered audio dubbing API using OpenAI for transcription, translation, and TTS",
    version=settings.api_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(FileValidationError)
async def file_validation_error_handler(_request: Request, exc: FileValidationError) -> JSONResponse:
    """Handle file validation errors.

    Args:
        request: Request object
        exc: Exception instance

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": exc.message,
            "error_code": "FILE_VALIDATION_ERROR",
            "errors": exc.details,
        },
    )


@app.exception_handler(AudioProcessingError)
async def audio_processing_error_handler(
    _request: Request, exc: AudioProcessingError
) -> JSONResponse:
    """Handle audio processing errors.

    Args:
        request: Request object
        exc: Exception instance

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": exc.message,
            "error_code": "AUDIO_PROCESSING_ERROR",
            "errors": exc.details,
        },
    )


@app.exception_handler(TranscriptionError)
async def transcription_error_handler(_request: Request, exc: TranscriptionError) -> JSONResponse:
    """Handle transcription errors.

    Args:
        request: Request object
        exc: Exception instance

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": exc.message,
            "error_code": "TRANSCRIPTION_ERROR",
            "errors": exc.details,
        },
    )


@app.exception_handler(TranslationError)
async def translation_error_handler(_request: Request, exc: TranslationError) -> JSONResponse:
    """Handle translation errors.

    Args:
        request: Request object
        exc: Exception instance

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": exc.message,
            "error_code": "TRANSLATION_ERROR",
            "errors": exc.details,
        },
    )


@app.exception_handler(TTSError)
async def tts_error_handler(_request: Request, exc: TTSError) -> JSONResponse:
    """Handle TTS generation errors.

    Args:
        request: Request object
        exc: Exception instance

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": exc.message,
            "error_code": "TTS_ERROR",
            "errors": exc.details,
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException) -> JSONResponse:
    """Handle HTTP exceptions.

    Args:
        request: Request object
        exc: Exception instance

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "error_code": "HTTP_ERROR",
        },
    )


# Include routers
app.include_router(health.router)
app.include_router(audio.router, prefix=f"/api/{settings.api_version}")


@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    """Root endpoint redirect to docs.

    Returns:
        Redirect message
    """
    return {
        "message": f"Welcome to {settings.app_name}",
        "docs": "/docs",
        "version": settings.api_version,
    }
