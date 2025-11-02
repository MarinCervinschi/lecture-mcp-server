from typing import Dict, Optional, List
from app.models.mcp import ToolSchema
from app.mcp_tools.tools import get_all_tools
import logging

logger = logging.getLogger(__name__)


class MCPToolRegistry:
    """
    Registry for MCP tools.

    Manages tool registration, discovery, and retrieval.
    """

    def __init__(self):
        """Initialize the registry and load default tools."""
        self._tools: Dict[str, ToolSchema] = {}
        self._register_default_tools()

    def _register_default_tools(self) -> None:
        """Register all default tools from mcp_tools module."""
        tools = get_all_tools()

        for tool in tools:
            self._register_tool(tool)

        logger.info(f"Registered {len(self._tools)} default MCP tools")

    def _register_tool(self, tool: ToolSchema) -> None:
        """
        Register a new tool.

        Args:
            tool: Tool schema to register
        """
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting")

        self._tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get_tool(self, name: str) -> Optional[ToolSchema]:
        """
        Get a tool by name.

        Args:
            name: Tool name

        Returns:
            Optional[ToolSchema]: Tool schema if found, None otherwise
        """
        return self._tools.get(name)

    def list_tools(self) -> List[ToolSchema]:
        """
        List all registered tools.

        Returns:
            List[ToolSchema]: List of all registered tools
        """
        return list(self._tools.values())

    def tool_exists(self, name: str) -> bool:
        """
        Check if a tool exists.

        Args:
            name: Tool name

        Returns:
            bool: True if tool exists, False otherwise
        """
        return name in self._tools


mcp_registry = MCPToolRegistry()
