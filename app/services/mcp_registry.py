import logging
from typing import Any, Dict, List, Optional

from mcp.types import Tool as MCPTool

from app.tools.base import BaseMCPTool as Tool
from app.tools.filter_content import FilterContentTool
from app.tools.pdf_to_text import PDFToTextTool
from app.tools.text_to_markdown import TextToMarkdownTool

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """Registry for MCP tools."""

    def __init__(self):
        """Initialize the registry and load default tools."""
        self._tools: Dict[str, Tool] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register all default tools."""
        tools: List[Tool] = [
            PDFToTextTool(),
            TextToMarkdownTool(),
            FilterContentTool(),
        ]

        for tool in tools:
            self._tools[tool.name] = tool

        logger.info(f"Registered {len(self._tools)} default MCP tools")

    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Optional[Tool]: Tool instance if found, None otherwise
        """
        return self._tools.get(name)

    def list_tools(self) -> List[MCPTool]:
        """
        List all tool schemas in MCP SDK format.

        Returns:
            List[MCPTool]: List of SDK tool schemas
        """
        return [tool.schema for tool in self._tools.values()]

    async def execute_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            args: Tool arguments

        Returns:
            Dict: Execution result

        Raises:
            ValueError: If tool not found
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError()

        return await tool.execute(args)


from functools import lru_cache


@lru_cache(maxsize=1)
def get_mcp_registry() -> MCPToolRegistry:
    """Get or create MCPToolRegistry singleton."""
    return MCPToolRegistry()
