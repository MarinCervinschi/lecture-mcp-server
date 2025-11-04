import logging
from typing import Dict, List, Optional

from app.mcp_tools.base import Tool
from app.mcp_tools.filter_content import FilterContentTool
from app.mcp_tools.pdf_to_text import PDFToTextTool
from app.mcp_tools.text_to_markdown import TextToMarkdownTool
from app.models.mcp import ToolExecutionResult, ToolSchema

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """Registry for MCP tools."""

    def __init__(self):
        """Initialize the registry and load default tools."""
        self._tools: Dict[str, Tool] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register all default tools."""
        tools = [
            PDFToTextTool(),
            FilterContentTool(),
            TextToMarkdownTool(),
        ]

        for tool in tools:
            self.register_tool(tool)

        logger.info(f"Registered {len(self._tools)} default MCP tools")

    def register_tool(self, tool: Tool) -> None:
        """
        Register a new tool.

        Args:
            tool: Tool instance to register
        """
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting")

        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Optional[Tool]: Tool instance if found, None otherwise
        """
        return self._tools.get(name)

    def get_tool_schema(self, name: str) -> Optional[ToolSchema]:
        """
        Get a tool schema by name.

        Args:
            name: Tool name

        Returns:
            Optional[ToolSchema]: Tool schema if found, None otherwise
        """
        tool = self.get_tool(name)
        return tool.schema if tool else None

    def list_tools(self) -> List[Tool]:
        """
        List all registered tools.

        Returns:
            List[Tool]: List of all registered tools
        """
        return list(self._tools.values())

    def list_tool_schemas(self) -> List[ToolSchema]:
        """
        List all tool schemas.

        Returns:
            List[ToolSchema]: List of all tool schemas
        """
        return [tool.schema for tool in self._tools.values()]

    async def execute_tool(self, name: str, parameters: Dict) -> ToolExecutionResult:
        """
        Execute a tool by name.

        Args:
            name: Tool name
            parameters: Tool parameters

        Returns:
            Dict: Execution result

        Raises:
            ValueError: If tool not found
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")

        return await tool.run(parameters)


from functools import lru_cache


@lru_cache(maxsize=1)
def get_mcp_registry() -> MCPToolRegistry:
    """Get or create MCPToolRegistry singleton."""
    return MCPToolRegistry()
