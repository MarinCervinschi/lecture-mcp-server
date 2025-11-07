import logging
from typing import Any, Dict

from mcp.types import Tool as MCPTool

from app.services.gemini_client import GeminiAPIError, get_gemini_client
from app.tools.base import BaseMCPTool

logger = logging.getLogger(__name__)

from pydantic import BaseModel, Field


class TextToMarkdownArgs(BaseModel):
    content: str = Field(..., min_length=1)


class TextToMarkdownResult(BaseModel):
    markdown: str = Field(..., description="Formatted Markdown content")


class TextToMarkdownTool(BaseMCPTool):
    """Tool for formatting text as clean Markdown."""

    def __init__(self):
        super().__init__()
        self.gemini_client = get_gemini_client()
        self.prompt = self.get_prompt()

    def _create_schema(self) -> MCPTool:
        """Create tool schema."""
        return MCPTool(
            name="text_to_markdown",
            description="Convert plain text to well-formatted Markdown with LaTeX support",
            inputSchema=TextToMarkdownArgs.model_json_schema(),
            outputSchema=TextToMarkdownResult.model_json_schema(),
        )

    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute text to Markdown conversion.

        Args:
            args: Tool parameters including content

        Returns:
            TextToMarkdownResult with formatted Markdown converted to dict
        """
        logger.info("Executing text to Markdown conversion")

        validated_params = TextToMarkdownArgs(**args)
        content = validated_params.content

        try:
            markdown = await self._convert_to_markdown(content)
            result = TextToMarkdownResult(
                markdown=markdown,
            )
            return result.model_dump()
        except GeminiAPIError as e:
            logger.error(f"Markdown conversion failed: {str(e)}")
            raise

    async def _convert_to_markdown(
        self,
        content: str,
    ) -> str:
        """
        Convert text to Markdown format.

        Args:
            content: Text content to convert

        Returns:
            str: Formatted Markdown

        Raises:
            GeminiError: If conversion fails
        """

        logger.info(f"Converting {len(content)} chars to Markdown")

        try:
            prompt = self.prompt.replace("{content}", content)

            response = await self.gemini_client.generate_with_retry(
                prompt=prompt,
                temperature=0.3,
                max_tokens=8000,
            )

            markdown = response.content.strip()

            logger.info(f"Conversion complete: {len(markdown)} chars")

            return markdown

        except GeminiAPIError as e:
            logger.error(f"Markdown conversion failed: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error in conversion: {str(e)}", exc_info=True)
            raise GeminiAPIError(f"Conversion failed: {str(e)}")
