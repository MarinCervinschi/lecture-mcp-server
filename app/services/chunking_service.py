import logging
from dataclasses import dataclass
from typing import List, Optional

from app.models.pdf import PDFChunk, PDFPage
from app.utils.token_counter import get_token_counter

logger = logging.getLogger(__name__)


@dataclass
class ChunkingConfig:
    """Configuration for document chunking."""

    max_tokens: int = 8000  # Safe limit for Gemini (has 30k context)
    overlap_tokens: int = 200  # Tokens to overlap between chunks
    target_tokens: int = 6000  # Target size (leaves room for prompt)
    min_chunk_tokens: int = 1000  # Minimum viable chunk size
    prefer_page_boundaries: bool = True  # Try to keep pages together


class ChunkingService:
    """
    Service for intelligent document chunking.
    """

    def __init__(self):
        self.config = ChunkingConfig()
        self.token_counter = get_token_counter()
        logger.info(
            f"Initialized ChunkingService with max_tokens={self.config.max_tokens}, "
            f"overlap={self.config.overlap_tokens}"
        )

    def chunk_pages(self, pages: List[PDFPage]) -> List[PDFChunk]:
        """
        Chunk PDF pages intelligently based on token counts.

        Args:
            pages: List of extracted PDF pages

        Returns:
            List[PDFChunk]: Optimized chunks with metadata
        """

        if not pages:
            logger.warning("No pages to chunk")
            return []

        logger.info(f"Chunking {len(pages)} pages with token-based strategy")

        page_tokens = self._calculate_page_tokens(pages)

        chunks = self._create_chunks_with_overlap(pages, page_tokens)

        logger.info(
            f"Created {len(chunks)} chunks (avg {sum(c.token_count for c in chunks) // len(chunks)} tokens/chunk)"
        )

        return chunks

    def _calculate_page_tokens(self, pages: List[PDFPage]) -> List[int]:
        """Calculate token count for each page."""
        token_counts = []

        for page in pages:
            tokens = self.token_counter.count_tokens(page.text)
            token_counts.append(tokens)
            logger.debug(f"Page {page.page_number}: {tokens} tokens")

        return token_counts

    def _create_chunks_with_overlap(
        self, pages: List[PDFPage], page_tokens: List[int]
    ) -> List[PDFChunk]:
        """
        Create chunks with intelligent overlap.

        Strategy:
        1. Try to fit pages within target token limit
        2. Add overlap from previous chunk for context
        3. Keep page boundaries when possible
        4. Split large pages if necessary
        """
        chunks = []
        current_pages = []
        current_tokens = 0
        overlap_content = None

        i = 0
        while i < len(pages):
            page = pages[i]
            page_token_count = page_tokens[i]

            if (
                current_tokens + page_token_count > self.config.target_tokens
                and current_pages
            ):
                chunk = self._create_chunk_from_pages(
                    chunks_so_far=len(chunks),
                    pages=current_pages,
                    overlap_content=overlap_content,
                )
                chunks.append(chunk)

                overlap_content = self._extract_overlap(current_pages)

                current_pages = []
                current_tokens = 0

            # Handle very large single page
            if page_token_count > self.config.max_tokens:
                logger.warning(
                    f"Page {page.page_number} has {page_token_count} tokens "
                    f"(exceeds max {self.config.max_tokens}), will split"
                )
                if current_pages:
                    chunk = self._create_chunk_from_pages(
                        chunks_so_far=len(chunks),
                        pages=current_pages,
                        overlap_content=overlap_content,
                    )
                    chunks.append(chunk)
                    current_pages = []
                    current_tokens = 0

                page_chunks = self._split_large_page(page)
                chunks.extend(page_chunks)
                overlap_content = page_chunks[-1].content[
                    -self.config.overlap_tokens * 4 :
                ]  # Approx chars
            else:
                # Add page to current chunk
                current_pages.append(page)
                current_tokens += page_token_count

            i += 1

        # Create final chunk if there are remaining pages
        if current_pages:
            chunk = self._create_chunk_from_pages(
                chunks_so_far=len(chunks),
                pages=current_pages,
                overlap_content=overlap_content,
            )
            chunks.append(chunk)

        return chunks

    def _create_chunk_from_pages(
        self,
        chunks_so_far: int,
        pages: List[PDFPage],
        overlap_content: Optional[str],
    ) -> PDFChunk:
        """Create a chunk from a list of pages."""
        content_parts = []

        for page in pages:
            if page.text.strip():
                content_parts.append(f"=== Page {page.page_number} ===\n{page.text}")

        content = "\n\n".join(content_parts)

        full_content = content
        has_overlap = False
        if overlap_content and chunks_so_far > 0:
            full_content = f"[Previous context...]\n{overlap_content}\n\n{content}"
            has_overlap = True

        token_count = self.token_counter.count_tokens(full_content)
        page_numbers = [p.page_number for p in pages]
        page_range = self._format_page_range(page_numbers)

        return PDFChunk(
            chunk_index=chunks_so_far,
            content=full_content,
            token_count=token_count,
            char_count=len(full_content),
            page_range=page_range,
            page_numbers=page_numbers,
            has_overlap=has_overlap,
            overlap_content=overlap_content if has_overlap else None,
        )

    def _extract_overlap(self, pages: List[PDFPage]) -> str:
        """
        Extract overlap content from end of pages.

        Takes last N tokens from the chunk to use as context for next chunk.
        """
        if not pages:
            return ""

        # Get last page(s) content
        combined_text = "\n\n".join(
            p.text for p in pages[-2:] if p.text.strip()  # Last 1-2 pages
        )

        # Take last N tokens
        overlap = self.token_counter.truncate_to_tokens(
            combined_text, max_tokens=self.config.overlap_tokens, add_ellipsis=False
        )

        # Try to find a good boundary (end of sentence)
        sentences = overlap.split(". ")
        if len(sentences) > 1:
            # Take last complete sentences
            overlap = ". ".join(sentences[-3:])  # Last 2-3 sentences

        return overlap

    def _split_large_page(self, page: PDFPage) -> List[PDFChunk]:
        """
        Split a single large page into multiple chunks.

        Used when a single page exceeds max_tokens.
        """
        chunks = []
        text = page.text

        # Split by paragraphs first
        paragraphs = text.split("\n\n")

        current_chunk_text = []
        current_tokens = 0

        for para in paragraphs:
            para_tokens = self.token_counter.count_tokens(para)

            if (
                current_tokens + para_tokens > self.config.target_tokens
                and current_chunk_text
            ):
                # Create chunk
                chunk_content = "\n\n".join(current_chunk_text)
                chunks.append(
                    PDFChunk(
                        chunk_index=len(chunks),
                        content=f"=== Page {page.page_number} (part {len(chunks) + 1}) ===\n{chunk_content}",
                        token_count=current_tokens,
                        char_count=len(chunk_content),
                        page_range=f"{page.page_number}",
                        page_numbers=[page.page_number],
                        has_overlap=False,
                    )
                )
                current_chunk_text = []
                current_tokens = 0

            current_chunk_text.append(para)
            current_tokens += para_tokens

        # Final chunk
        if current_chunk_text:
            chunk_content = "\n\n".join(current_chunk_text)
            chunks.append(
                PDFChunk(
                    chunk_index=len(chunks),
                    content=f"=== Page {page.page_number} (part {len(chunks) + 1}) ===\n{chunk_content}",
                    token_count=current_tokens,
                    char_count=len(chunk_content),
                    page_range=f"{page.page_number}",
                    page_numbers=[page.page_number],
                    has_overlap=False,
                )
            )

        logger.info(f"Split page {page.page_number} into {len(chunks)} chunks")
        return chunks

    def _format_page_range(self, page_numbers: List[int]) -> str:
        """Format page numbers as a range string."""
        if not page_numbers:
            return ""

        if len(page_numbers) == 1:
            return str(page_numbers[0])

        return f"{page_numbers[0]}-{page_numbers[-1]}"


from functools import lru_cache


@lru_cache(maxsize=1)
def get_chunking_service() -> ChunkingService:
    """Get or create ChunkingService singleton."""
    return ChunkingService()
