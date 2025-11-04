import logging
from typing import Any, Dict, List

from pydantic import BaseModel, Field

from app.mcp_tools.base import Tool
from app.models.mcp import (
    ToolParameter,
    ToolParameterType,
    ToolSchema,
)
from app.models.pdf import PDFChunk
from app.services.pdf_service import PDFProcessingError, get_pdf_service
from app.utils.file_utils import FileValidationError, validate_file

logger = logging.getLogger(__name__)


class PDFToTextParameters(BaseModel):
    """Parameters for PDF to text extraction tool."""

    file_data: str = Field(..., description="Base64 encoded PDF file content")


class PDFToTextResult(BaseModel):
    """Result of PDF to text extraction and chunking."""

    metadata: Dict[str, Any] = Field(
        ..., description="Metadata about the processed PDF"
    )
    total_chunks: int = Field(..., description="Total number of chunks created")
    chunks: List[PDFChunk] = Field(..., description="List of extracted PDF chunks")


class PDFToTextTool(Tool[PDFToTextResult]):
    """
    Extract text from PDF and split into LLM-ready chunks.

    This tool:
    - Extracts text from PDF pages
    - Splits content into token-optimized chunks
    - Adds overlap for context preservation
    - Returns structured data for client processing
    """

    def __init__(self):
        self.pdf_service = get_pdf_service()

    @property
    def schema(self) -> ToolSchema:
        """Get tool schema."""
        return ToolSchema(
            name="pdf_to_text",
            description=(
                "Extract text from PDF and chunk for LLM processing. "
                "Returns token-optimized chunks that fit within LLM context limits."
            ),
            version="2.0.0",
            parameters=[
                ToolParameter(
                    name="file_data",
                    type=ToolParameterType.FILE,
                    description="PDF file content (base64 encoded)",
                    required=True,
                    mime_types=["application/pdf"],
                )
            ],
        )

    async def execute(self, parameters: Dict[str, Any]) -> PDFToTextResult:
        """
        Extract PDF text and create LLM-ready chunks.

        Args:
            parameters: Tool parameters

        Returns:
            dict: Extracted chunks with metadata
        """
        logger.info("Executing PDF to text extraction with smart chunking")

        try:
            validated_params = PDFToTextParameters(**parameters)

            pdf_data = validate_file(
                validated_params.file_data, mime_type="application/pdf"
            )

            metadata = self.pdf_service.get_pdf_metadata(pdf_data)
            chunks = self.pdf_service.extract_text_chunked(pdf_data)

            pdf_result = PDFToTextResult(
                metadata=metadata,
                total_chunks=len(chunks),
                chunks=chunks,
            )

            logger.info(f"Extraction complete: {len(chunks)} chunks created from PDF")

            return pdf_result

        except (FileValidationError, PDFProcessingError, ValueError) as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise
