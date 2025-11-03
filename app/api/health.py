import logging
from datetime import datetime

from fastapi import APIRouter, status

from app.core.config import settings
from app.models.responses import HealthResponse
from app.services.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the service is running and dependencies are available",
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse: Service health status with dependency checks
    """
    gemini_status = "unknown"
    try:
        client = get_gemini_client()
        gemini_available = await client.test_connection()
        gemini_status = "available" if gemini_available else "unavailable"
    except Exception as e:
        logger.warning(f"Gemini health check failed: {str(e)}")
        gemini_status = "error"

    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        service=settings.PROJECT_NAME,
        dependencies={"gemini_api": gemini_status},
    )
