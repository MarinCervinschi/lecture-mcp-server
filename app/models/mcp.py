from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ToolParameterType(str, Enum):
    """Parameter types for MCP tools."""

    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"
    OBJECT = "object"
    ARRAY = "array"
    FILE = "file"


class ToolParameter(BaseModel):
    """Definition of a tool parameter."""

    name: str = Field(..., description="Parameter name")
    type: ToolParameterType = Field(..., description="Parameter type")
    description: str = Field(..., description="Parameter description")
    required: bool = Field(default=True, description="Whether parameter is required")
    default: Optional[Any] = Field(default=None, description="Default value")
    enum: Optional[List[str]] = Field(default=None, description="Allowed values")
    mime_types: Optional[List[str]] = Field(
        default=None, description="Accepted MIME types (for FILE type)"
    )
    max_size: Optional[int] = Field(
        default=None, description="Maximum size in bytes (for FILE type)"
    )


class ToolSchema(BaseModel):
    """Schema definition for an MCP tool."""

    name: str = Field(..., description="Unique tool identifier")
    description: str = Field(..., description="Tool description")
    version: str = Field(default="1.0.0", description="Tool version")
    parameters: List[ToolParameter] = Field(
        default_factory=list, description="Tool parameters"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "pdf_to_markdown",
                "description": "Convert PDF to structured Markdown",
                "version": "1.0.0",
                "parameters": [
                    {
                        "name": "file_data",
                        "type": "file",
                        "description": "PDF file content as base64 or bytes",
                        "required": True,
                        "mime_types": ["application/pdf"],
                        "max_size": 10485760,
                    }
                ],
            }
        }
    }


class ToolDiscoveryResponse(BaseModel):
    """Response for tool discovery endpoint."""

    tools: List[ToolSchema] = Field(..., description="Available tools")
    server_version: str = Field(..., description="MCP server version")
    protocol_version: str = Field(default="1.0", description="MCP protocol version")


class ToolExecutionRequest(BaseModel):
    """Request to execute a tool."""

    tool: str = Field(..., description="Tool name to execute")
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Tool execution parameters (file_data should be base64 encoded)",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "tool": "pdf_to_markdown",
                "parameters": {
                    "file_data": "JVBERi0xLjQKJeLjz9MK...",  # base64 encoded PDF
                    "filename": "lecture_01.pdf",  # optional, for reference
                    "preserve_latex": True,
                    "filter_level": 2,
                },
            }
        }
    }


class ToolExecutionStatus(str, Enum):
    """Status of tool execution."""

    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"
    RUNNING = "running"


class ToolExecutionResponse(BaseModel):
    """Response from tool execution."""

    status: ToolExecutionStatus = Field(..., description="Execution status")
    tool: str = Field(..., description="Tool that was executed")
    result: Optional[Dict[str, Any]] = Field(
        default=None, description="Execution result"
    )
    error: Optional[str] = Field(default=None, description="Error message if failed")
    execution_time: Optional[float] = Field(
        None, description="Execution time in seconds"
    )


class MCPError(BaseModel):
    """Standard MCP error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    details: Optional[Dict[str, Any]] = Field(
        None, description="Additional error details"
    )
