import logging
from typing import Any, Dict, List

from mcp.types import Tool as MCPTool
from pydantic import BaseModel, Field

from app.models.pdf import PDFChunk
from app.services.pdf_service import PDFProcessingError, get_pdf_service
from app.tools.base import BaseMCPTool
from app.utils.file_utils import FileValidationError, validate_file

logger = logging.getLogger(__name__)


class PDFToTextArgs(BaseModel):
    file_data: str = Field(..., description="Base64 encoded PDF file content")


class PDFToTextResult(BaseModel):
    metadata: Dict[str, Any] = Field(
        ..., description="Metadata about the processed PDF"
    )
    total_chunks: int = Field(..., description="Total number of chunks created")
    chunks: List[PDFChunk] = Field(..., description="List of extracted PDF chunks")


class PDFToTextTool(BaseMCPTool):
    """Extract text from PDF and split into LLM-ready chunks."""

    def __init__(self):
        super().__init__()
        self.pdf_service = get_pdf_service()

    def _create_schema(self) -> MCPTool:
        """Create tool schema."""

        return MCPTool(
            name="pdf_to_text",
            description=(
                "Extract text from PDF and chunk for LLM processing. "
                "Returns token-optimized chunks that fit within LLM context limits."
            ),
            inputSchema=PDFToTextArgs.model_json_schema(),
            outputSchema=PDFToTextResult.model_json_schema(),
        )

    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract PDF text and create LLM-ready chunks.

        Args:
            args: Tool parameters including base64 PDF data

        Returns:
            PDFToTextResult: Extracted chunks with metadata convered to dict
        """
        logger.info("Executing PDF to text extraction with smart chunking")

        try:
            validated_params = PDFToTextArgs(**args)

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

            return pdf_result.model_dump()

        except (FileValidationError, PDFProcessingError, ValueError) as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise
