from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timezone


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service health status")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    version: str = Field(..., description="API version")
    service: str = Field(..., description="Service name")


class ErrorResponse(BaseModel):
    """Standard error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str = Field(..., description="Response message")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional data")