import logging
from typing import Any, Dict, List

from app.mcp_tools.base import Tool
from app.models.mcp import (
    ToolExecutionResult,
    ToolParameter,
    ToolParameterType,
    ToolSchema,
)
from app.models.pdf import PDFChunk
from app.services.chunking_service import get_chunking_service
from app.services.pdf_service import PDFProcessingError, pdf_service
from app.utils.file_utils import FileValidationError, validate_file

logger = logging.getLogger(__name__)


class PDFToTextResult(ToolExecutionResult):
    """Result of PDF to text extraction and chunking."""

    metadata: Dict[str, Any]
    total_chunks: int
    statistics: Dict[str, Any]
    chunks: List[PDFChunk]


class PDFToTextTool(Tool):
    """
    Extract text from PDF and split into LLM-ready chunks.

    This tool:
    - Extracts text from PDF pages
    - Splits content into token-optimized chunks
    - Adds overlap for context preservation
    - Returns structured data for client processing
    """

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
            pdf_data = validate_file(
                parameters["file_data"], mime_type="application/pdf", strict_mime=True
            )

            metadata = pdf_service.get_pdf_metadata(pdf_data)
            chunks = pdf_service.extract_text_chunked(pdf_data)

            chunking_service = get_chunking_service()
            stats = chunking_service.analyze_chunking_stats(chunks)

            pdf_result = PDFToTextResult(
                metadata=metadata,
                total_chunks=len(chunks),
                statistics={
                    "total_tokens": stats["total_tokens"],
                    "avg_tokens_per_chunk": stats["avg_tokens_per_chunk"],
                    "token_range": {
                        "min": stats["min_tokens"],
                        "max": stats["max_tokens"],
                    },
                    "chunks_with_overlap": stats["chunks_with_overlap"],
                    "avg_pages_per_chunk": round(stats["avg_pages_per_chunk"], 1),
                },
                chunks=chunks,
            )

            logger.info(
                f"Extraction complete: {len(chunks)} chunks, "
                f"{stats['total_tokens']} total tokens, "
                f"avg {stats['avg_tokens_per_chunk']} tokens/chunk"
            )

            return pdf_result

        except (FileValidationError, PDFProcessingError, ValueError) as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}", exc_info=True)
            raise
