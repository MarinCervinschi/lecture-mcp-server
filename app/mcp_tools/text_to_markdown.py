import logging
from typing import Any, Dict

from app.mcp_tools.base import Tool
from app.models.mcp import ToolParameter, ToolParameterType, ToolSchema

logger = logging.getLogger(__name__)


class TextToMarkdownTool(Tool):
    """Tool for formatting text as clean Markdown."""

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
                ToolParameter(
                    name="preserve_latex",
                    type=ToolParameterType.BOOLEAN,
                    description="Whether to preserve LaTeX formulas",
                    required=False,
                    default=True,
                ),
                ToolParameter(
                    name="source_format",
                    type=ToolParameterType.STRING,
                    description="Source format hint (plain, extracted_pdf, etc.)",
                    required=False,
                    default="plain",
                    enum=["plain", "extracted_pdf", "ocr", "transcript"],
                ),
            ],
        )

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute text to Markdown conversion.

        Args:
            parameters: Tool parameters including content, preserve_latex

        Returns:
            Dict with formatted Markdown content
        """
        logger.info("Executing text to Markdown conversion")

        content = parameters["content"]
        preserve_latex = parameters.get("preserve_latex", True)
        source_format = parameters.get("source_format", "plain")

        # TODO: Implement actual formatting logic with Gemini
        # For now, return basic formatted version
        markdown = self._basic_format(content, preserve_latex)

        return {
            "original_length": len(content),
            "markdown_length": len(markdown),
            "preserve_latex": preserve_latex,
            "source_format": source_format,
            "markdown": markdown,
        }

    def _basic_format(self, content: str, preserve_latex: bool) -> str:
        """
        Basic Markdown formatting (placeholder).

        TODO: Replace with Gemini-based formatting
        """
        # Simple placeholder implementation
        lines = content.split("\n")
        formatted = []

        for line in lines:
            stripped = line.strip()

            # Detect potential headers (all caps or short lines)
            if stripped and stripped.isupper() and len(stripped) < 50:
                formatted.append(f"## {stripped.title()}\n")
            elif stripped:
                formatted.append(stripped)

        return "\n\n".join(formatted)
