import logging
from typing import Any, Dict

from app.core.config import settings
from app.mcp_tools.base import Tool
from app.models.mcp import ToolParameter, ToolParameterType, ToolSchema
from app.services.pdf_service import PDFProcessingError, pdf_service
from app.utils.file_utils import FileValidationError, validate_file

logger = logging.getLogger(__name__)


class PDFToTextTool(Tool):
    """Tool for extracting text from PDF files."""

    @property
    def schema(self) -> ToolSchema:
        """Get tool schema."""
        return ToolSchema(
            name="pdf_to_text",
            description="Extract text from PDF file with chunking support",
            version="1.0.0",
            parameters=[
                ToolParameter(
                    name="file_data",
                    type=ToolParameterType.FILE,
                    description="PDF file content (base64 encoded string or bytes)",
                    required=True,
                    mime_types=["application/pdf"],
                    max_size=settings.MAX_FILE_SIZE,
                ),
                ToolParameter(
                    name="chunk_size",
                    type=ToolParameterType.INTEGER,
                    description="Number of pages per chunk",
                    required=False,
                    default=10,
                ),
                ToolParameter(
                    name="page_range",
                    type=ToolParameterType.STRING,
                    description="Page range to extract (e.g., '1-5', 'all')",
                    required=False,
                    default="all",
                ),
            ],
        )

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute PDF text extraction.

        Args:
            parameters: Tool parameters including file_data, chunk_size, page_range

        Returns:
            Dict with extracted text chunks and metadata

        Raises:
            FileValidationError: If file validation fails
            PDFProcessingError: If PDF processing fails
        """
        logger.info("Executing PDF to text extraction")

        try:
            pdf_data = validate_file(
                parameters["file_data"], mime_type="application/pdf", strict_mime=False
            )

            chunk_size = parameters.get("chunk_size", 10)
            page_range = parameters.get("page_range", "all")

            metadata = pdf_service.get_pdf_metadata(pdf_data)
            logger.info(f"PDF metadata: {metadata}")

            chunks = pdf_service.extract_text_chunked(pdf_data, chunk_size=chunk_size)

            result = {
                "metadata": metadata,
                "total_pages": metadata["page_count"],
                "total_chunks": len(chunks),
                "chunks": [
                    {
                        "chunk_index": chunk.chunk_index,
                        "page_range": chunk.page_range,
                        "text": chunk.total_text,
                        "char_count": chunk.char_count,
                        "page_count": len(chunk.pages),
                    }
                    for chunk in chunks
                ],
            }

            logger.info(
                f"Extracted {metadata['page_count']} pages in {len(chunks)} chunks"
            )

            return result

        except (FileValidationError, PDFProcessingError) as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise PDFProcessingError(f"Failed to extract text from PDF: {str(e)}")
