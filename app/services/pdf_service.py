import io
import logging
from dataclasses import dataclass
from typing import Any, Dict, List

import pdfplumber

logger = logging.getLogger(__name__)


class PDFProcessingError(Exception):
    """Raised when PDF processing fails."""

    pass


@dataclass
class PDFPage:
    """Represents a single PDF page with extracted content."""

    page_number: int
    text: str
    width: float
    height: float
    char_count: int


@dataclass
class PDFChunk:
    """Represents a chunk of PDF pages."""

    chunk_index: int
    page_range: str  # e.g., "1-10"
    pages: List[PDFPage]
    total_text: str
    char_count: int


class PDFService:
    """Service for PDF text extraction and processing."""

    def __init__(self):
        self.max_text_length = 1000000  # 1MB of text

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
                        # Extract text from page
                        text = page.extract_text() or ""

                        # Get page dimensions
                        width = page.width
                        height = page.height

                        pdf_page = PDFPage(
                            page_number=page_num,
                            text=text.strip(),
                            width=width,
                            height=height,
                            char_count=len(text),
                        )

                        pages.append(pdf_page)
                        logger.debug(f"Extracted page {page_num}: {len(text)} chars")

                    except Exception as e:
                        logger.warning(f"Failed to extract page {page_num}: {str(e)}")
                        # Add empty page to maintain page numbers
                        pages.append(
                            PDFPage(
                                page_number=page_num,
                                text="",
                                width=0,
                                height=0,
                                char_count=0,
                            )
                        )

                logger.info(f"Successfully extracted {len(pages)} pages")
                return pages

        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}", exc_info=True)
            raise PDFProcessingError(f"Failed to extract text from PDF: {str(e)}")

    def extract_text_chunked(
        self, pdf_data: bytes, chunk_size: int = 10
    ) -> List[PDFChunk]:
        """
        Extract text from PDF in chunks.

        Args:
            pdf_data: PDF file as bytes
            chunk_size: Number of pages per chunk

        Returns:
            List[PDFChunk]: List of page chunks

        Raises:
            PDFProcessingError: If extraction fails
        """
        all_pages = self.extract_text(pdf_data)

        chunks = []
        total_pages = len(all_pages)

        for i in range(0, total_pages, chunk_size):
            chunk_pages = all_pages[i : i + chunk_size]

            # Calculate page range
            start_page = chunk_pages[0].page_number
            end_page = chunk_pages[-1].page_number
            page_range = (
                f"{start_page}-{end_page}"
                if start_page != end_page
                else str(start_page)
            )

            # Combine all text in chunk
            total_text = "\n\n".join(
                f"=== Page {p.page_number} ===\n{p.text}"
                for p in chunk_pages
                if p.text  # Skip empty pages
            )

            chunk = PDFChunk(
                chunk_index=len(chunks),
                page_range=page_range,
                pages=chunk_pages,
                total_text=total_text,
                char_count=len(total_text),
            )

            chunks.append(chunk)
            logger.debug(
                f"Created chunk {chunk.chunk_index}: "
                f"pages {page_range}, {chunk.char_count} chars"
            )

        logger.info(f"Created {len(chunks)} chunks from {total_pages} pages")
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

    def validate_pdf(self, pdf_data: bytes) -> bool:
        """
        Validate if data is a valid PDF.

        Args:
            pdf_data: PDF file as bytes

        Returns:
            bool: True if valid PDF
        """
        try:
            pdf_file = io.BytesIO(pdf_data)
            with pdfplumber.open(pdf_file) as pdf:
                # Try to access pages
                _ = len(pdf.pages)
            return True
        except Exception as e:
            logger.warning(f"PDF validation failed: {str(e)}")
            return False


pdf_service = PDFService()
