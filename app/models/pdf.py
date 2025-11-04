from dataclasses import dataclass
from typing import Any, Dict, List, Optional


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
    content: str
    token_count: int
    char_count: int
    page_range: str  # e.g., "1-5"
    page_numbers: List[int]
    has_overlap: bool
    overlap_content: Optional[str] = None
