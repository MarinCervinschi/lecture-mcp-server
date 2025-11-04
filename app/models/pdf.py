from typing import Optional

from pydantic import BaseModel, Field, computed_field


class PDFProcessingError(Exception):
    """Raised when PDF processing fails."""

    pass


class PDFPage(BaseModel):
    """Represents a single PDF page with extracted content."""

    page_number: int = Field(ge=1, description="Page number (1-indexed)")
    text: str = Field(description="Extracted text content")
    char_count: int = Field(ge=0, description="Character count")


class PDFChunk(BaseModel):
    """Represents a chunk of PDF content optimized for LLM processing."""

    chunk_index: int = Field(ge=0, description="Chunk index (0-based)")
    content: str = Field(min_length=1, description="Main chunk content")
    token_count: int = Field(gt=0, description="Approximate token count")
    char_count: int = Field(gt=0, description="Character count")
    page_range: str = Field(description="Source page range (e.g., '1-5', '3')")
    has_overlap: bool = Field(
        description="Whether this chunk includes overlap from previous chunk"
    )
    overlap_content: Optional[str] = Field(
        default=None, description="Overlap from previous chunk for context preservation"
    )
