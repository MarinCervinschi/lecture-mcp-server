import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

logger = logging.getLogger(__name__)

from mcp.types import Tool as MCPTool


class BaseMCPTool(ABC):
    """
    Abstract base class for MCP tools.

    Each tool must implement:
    - _create_schema() method: Defines the tool schema
    - execute() method: Executes the tool logic
    """

    def __init__(self) -> None:
        self._schema: MCPTool = self._create_schema()

    @property
    def name(self) -> str:
        """Get tool name from schema."""
        return self._schema.name

    @property
    def schema(self) -> MCPTool:
        """Get tool schema."""
        return self._schema

    @abstractmethod
    def _create_schema(self) -> MCPTool:
        """
        Create MCP tool schema.

        Returns:
            MCPTool: Tool schema definition
        """
        pass

    @abstractmethod
    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool.

        Args:
            args: Tool arguments

        Returns:
            Any: Tool execution result
        """
        pass

    def get_prompt(self) -> str:
        """
        Get tool prompt from file.

        Returns:
            str: Tool prompt description
        """

        try:
            with open(f"app/prompts/{self.name}.md", "r") as f:
                prompt = f.read()
        except FileNotFoundError:
            raise ValueError(f"Prompt file for tool '{self.name}' not found.")

        return prompt
