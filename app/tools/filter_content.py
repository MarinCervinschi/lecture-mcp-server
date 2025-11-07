import logging
from typing import Any, Dict

from mcp.types import Tool as MCPTool
from pydantic import BaseModel, Field

from app.services.gemini_client import GeminiAPIError, get_gemini_client
from app.tools.base import BaseMCPTool

logger = logging.getLogger(__name__)


class FilterContentArgs(BaseModel):
    content: str = Field(..., min_length=1)


class FilterContentResult(BaseModel):
    filtered_content: str = Field(..., description="Cleaned text with noise removed")


class FilterContentTool(BaseMCPTool):
    """Tool for filtering irrelevant content from text."""

    def __init__(self):
        super().__init__()
        self.gemini_client = get_gemini_client()
        self.prompt = self.get_prompt()

    def _create_schema(self) -> MCPTool:
        """Create tool schema."""
        return MCPTool(
            name="filter_content",
            description="Remove noise and irrelevant content from any text",
            inputSchema=FilterContentArgs.model_json_schema(),
            outputSchema=FilterContentResult.model_json_schema(),
        )

    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content filtering.

        Args:
            args: Tool parameters including content

        Returns:
            FilterContentResult with filtered content converted to dict
        """
        logger.info("Executing content filtering")

        validated_params = FilterContentArgs(**args)
        content = validated_params.content

        try:
            filtered_content = await self._filter_content(content)
            result = FilterContentResult(
                filtered_content=filtered_content,
            )
            return result.model_dump()
        except GeminiAPIError as e:
            logger.error(f"Content filtering failed: {str(e)}")
            raise

    async def _filter_content(self, content: str) -> str:
        """
        Filter irrelevant content from text.

        Args:
            content: Text content to filter

        Returns:
            str: Filtered content

        Raises:
            GeminiAPIError: If filtering fails
        """
        logger.info(f"Filtering {len(content)} chars")

        try:
            prompt = self.prompt.replace("{content}", content)

            response = await self.gemini_client.generate_with_retry(
                prompt=prompt,
                temperature=0.3,
                max_tokens=8000,
            )

            filtered = response.content.strip()

            logger.info(f"Filtering complete: {len(filtered)} chars")

            return filtered

        except GeminiAPIError as e:
            logger.error(f"Content filtering failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in filtering: {str(e)}", exc_info=True)
            raise GeminiAPIError(f"Filtering failed: {str(e)}")
