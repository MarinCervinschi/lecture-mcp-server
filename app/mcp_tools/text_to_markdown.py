import logging
from typing import Any, Dict

from app.mcp_tools.base import Tool
from app.models.mcp import ToolParameter, ToolParameterType, ToolSchema
from app.services.gemini_client import GeminiAPIError, get_gemini_client

logger = logging.getLogger(__name__)

from pydantic import BaseModel, Field


class TextToMardownParameters(BaseModel):
    """Parameters for text to Markdown conversion tool."""

    content: str = Field(..., min_length=1)


class TextToMarkdownResult(BaseModel):
    """Result of text to Markdown conversion."""

    markdown: str = Field(..., description="Formatted Markdown content")


class TextToMarkdownTool(Tool[TextToMarkdownResult]):
    """Tool for formatting text as clean Markdown."""

    def __init__(self):
        self.gemini_client = get_gemini_client()
        self.prompt = self.get_prompt()

    @property
    def schema(self) -> ToolSchema:
        """Get tool schema."""
        return ToolSchema(
            name="text_to_markdown",
            description="Convert plain text to well-formatted Markdown with LaTeX support",
            version="1.0.0",
            parameters=[
                ToolParameter(
                    name="content",
                    type=ToolParameterType.STRING,
                    description="Plain text content to convert to Markdown",
                    required=True,
                ),
            ],
        )

    async def execute(self, parameters: Dict[str, Any]) -> TextToMarkdownResult:
        """
        Execute text to Markdown conversion.

        Args:
            parameters: Tool parameters including content

        Returns:
            Dict with formatted Markdown content
        """
        logger.info("Executing text to Markdown conversion")

        validated_params = TextToMardownParameters(**parameters)

        content = validated_params.content

        try:
            markdown = await self._convert_to_markdown(content)
            return TextToMarkdownResult(
                markdown=markdown,
            )
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
