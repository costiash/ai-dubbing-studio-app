"""Health check endpoint."""

from fastapi import APIRouter, Depends

from backend.core.config import settings
from backend.schemas.audio import HealthResponse
from backend.services.openai_client import OpenAIService, get_openai_service

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Check API health and OpenAI configuration status",
)
async def health_check(
    openai_service: OpenAIService = Depends(get_openai_service),
) -> HealthResponse:
    """Check API health status.

    Returns:
        Health status including OpenAI API configuration
    """
    return HealthResponse(
        status="healthy",
        openai_api_configured=bool(openai_service.api_key),
        version=settings.api_version,
    )
