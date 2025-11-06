import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from app.core.config import settings
from app.models.responses import HealthResponse
from app.services.gemini_client import GeminiClient, get_gemini_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the service is running and dependencies are available",
)
async def health_check(
    gemini: GeminiClient = Depends(get_gemini_client),
) -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse: Service health status with dependency checks
    """
    gemini_status = "unknown"
    try:
        gemini_available = await gemini.test_connection()
        gemini_status = "available" if gemini_available else "unavailable"
    except Exception as e:
        logger.warning(f"Gemini health check failed: {str(e)}")
        gemini_status = "error"

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc),
        version=settings.VERSION,
        service=settings.PROJECT_NAME,
        dependencies={"gemini_api": gemini_status},
    )
