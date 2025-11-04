import logging
from typing import Optional

import tiktoken

logger = logging.getLogger(__name__)


class TokenCounter:
    """
    Service for counting tokens in text.

    Uses tiktoken with cl100k_base encoding (used by GPT-4/Gemini).
    """

    def __init__(self, encoding_name: str = "cl100k_base"):
        """
        Initialize token counter.

        Args:
            encoding_name: Tiktoken encoding to use
                - "cl100k_base": GPT-4, GPT-3.5-turbo, Gemini
                - "p50k_base": GPT-3
                - "r50k_base": GPT-2
        """
        try:
            self.encoding = tiktoken.get_encoding(encoding_name)
            self.encoding_name = encoding_name
            logger.info(f"Initialized TokenCounter with encoding: {encoding_name}")
        except Exception as e:
            logger.error(f"Failed to load encoding: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            int: Number of tokens
        """
        if not text:
            return 0

        try:
            tokens = self.encoding.encode(text)
            return len(tokens)
        except Exception as e:
            logger.error(f"Token counting failed: {e}")
            # Fallback: estimate based on characters
            return len(text) // 4

    def truncate_to_tokens(
        self, text: str, max_tokens: int, add_ellipsis: bool = True
    ) -> str:
        """
        Truncate text to fit within token limit.

        Args:
            text: Text to truncate
            max_tokens: Maximum number of tokens
            add_ellipsis: Whether to add "..." at end

        Returns:
            str: Truncated text
        """
        if not text:
            return text

        try:
            tokens = self.encoding.encode(text)

            if len(tokens) <= max_tokens:
                return text

            # Truncate tokens
            truncated_tokens = tokens[:max_tokens]
            truncated_text = self.encoding.decode(truncated_tokens)

            if add_ellipsis:
                truncated_text += "..."

            logger.debug(f"Truncated text from {len(tokens)} to {max_tokens} tokens")

            return truncated_text

        except Exception as e:
            logger.error(f"Truncation failed: {e}")
            # Fallback: character-based truncation
            char_limit = max_tokens * 4
            return text[:char_limit] + ("..." if add_ellipsis else "")


_token_counter: Optional[TokenCounter] = None


def get_token_counter() -> TokenCounter:
    """Get or create TokenCounter instance."""
    global _token_counter

    if _token_counter is None:
        _token_counter = TokenCounter()

    return _token_counter
