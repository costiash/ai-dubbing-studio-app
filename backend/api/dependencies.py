"""FastAPI dependency injection functions."""

from backend.services.openai_client import OpenAIService, get_openai_service

__all__ = ["get_openai_service", "OpenAIService"]
