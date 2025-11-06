import io
import logging
from typing import Any, Dict, List

import pdfplumber

from app.models.pdf import PDFChunk, PDFPage, PDFProcessingError
from app.services.chunking_service import get_chunking_service

logging.getLogger("pdfplumber").setLevel(logging.ERROR)
logger = logging.getLogger(__name__)


class PDFService:
    """Service for PDF text extraction and processing."""

    def __init__(self):
        self.chunking_service = get_chunking_service()

    def extract_text(self, pdf_data: bytes) -> List[PDFPage]:
        """
        Extract text from all pages of a PDF.

        Args:
            pdf_data: PDF file as bytes

        Returns:
            List[PDFPage]: List of extracted pages

        Raises:
            PDFProcessingError: If extraction fails
        """
        try:
            pages = []
            pdf_file = io.BytesIO(pdf_data)

            with pdfplumber.open(pdf_file) as pdf:
                total_pages = len(pdf.pages)
                logger.info(f"Processing PDF with {total_pages} pages")

                for page_num, page in enumerate(pdf.pages, start=1):
                    try:
                        text = page.extract_text() or ""

                        pdf_page = PDFPage(
                            page_number=page_num,
                            text=text.strip(),
                            char_count=len(text),
                        )

                        pages.append(pdf_page)
                        logger.debug(f"Extracted page {page_num}: {len(text)} chars")

                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {str(e)}")
                        pages.append(
                            PDFPage(
                                page_number=page_num,
                                text="",
                                char_count=0,
                            )
                        )

                logger.info(f"Successfully extracted {len(pages)} pages")
                return pages

        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}", exc_info=True)
            raise PDFProcessingError(f"Failed to extract text from PDF: {str(e)}")

    def extract_text_chunked(self, pdf_data: bytes) -> List[PDFChunk]:
        """
        Extract text with intelligent token-based chunking.

        Args:
            pdf_data: PDF file as bytes
            chunking_config: Optional chunking configuration

        Returns:
            List[PDFChunk]: Optimized chunks with overlap
        """
        pages = self.extract_text(pdf_data)

        chunks = self.chunking_service.chunk_pages(pages)

        logger.info(f"Smart chunking: {len(pages)} pages → {len(chunks)} chunks")

        return chunks

    def get_pdf_metadata(self, pdf_data: bytes) -> Dict[str, Any]:
        """
        Extract metadata from PDF.

        Args:
            pdf_data: PDF file as bytes

        Returns:
            Dict with PDF metadata

        Raises:
            PDFProcessingError: If extraction fails
        """
        try:
            pdf_file = io.BytesIO(pdf_data)

            with pdfplumber.open(pdf_file) as pdf:
                metadata = pdf.metadata or {}

                return {
                    "page_count": len(pdf.pages),
                    "title": metadata.get("Title", ""),
                    "author": metadata.get("Author", ""),
                    "subject": metadata.get("Subject", ""),
                    "creator": metadata.get("Creator", ""),
                    "producer": metadata.get("Producer", ""),
                    "creation_date": metadata.get("CreationDate", ""),
                }

        except Exception as e:
            logger.error(f"Failed to extract metadata: {str(e)}")
            raise PDFProcessingError(f"Failed to extract PDF metadata: {str(e)}")


from functools import lru_cache


@lru_cache(maxsize=1)
def get_pdf_service() -> PDFService:
    """Get or create PDFService singleton."""
    return PDFService()
