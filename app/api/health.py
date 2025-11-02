from fastapi import APIRouter, status
from app.models.responses import HealthResponse
from app.core.config import settings
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the service is running and healthy"
)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.
    
    Returns:
        HealthResponse: Service health status
    """
    logger.debug("Health check requested")
    
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version=settings.VERSION,
        service=settings.PROJECT_NAME
    )


@router.get(
    "/ready",
    status_code=status.HTTP_200_OK,
    summary="Readiness Check",
    description="Check if the service is ready to accept requests"
)
async def readiness_check() -> dict:
    """
    Readiness check endpoint.
    
    Returns:
        dict: Readiness status with dependencies
    """
    checks = {
        "api": "ready",
        "gemini": "not_configured" if not settings.GEMINI_API_KEY else "ready",
    }
    
    all_ready = all(v == "ready" for v in checks.values())
    
    return {
        "status": "ready" if all_ready else "not_ready",
        "checks": checks,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }