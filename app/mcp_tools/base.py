from abc import ABC, abstractmethod
from typing import Dict, Any
from app.models.mcp import ToolSchema
import logging

logger = logging.getLogger(__name__)


class Tool(ABC):
    """
    Abstract base class for MCP tools.

    Each tool must implement:
    - schema() property: Returns ToolSchema definition
    - execute() method: Executes the tool logic
    """

    @property
    @abstractmethod
    def schema(self) -> ToolSchema:
        """
        Get the tool schema definition.

        Returns:
            ToolSchema: Tool schema with parameters
        """
        pass

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the tool with given parameters.

        Args:
            parameters: Tool execution parameters

        Returns:
            Dict[str, Any]: Execution result

        Raises:
            Exception: If execution fails
        """
        pass

    @property
    def name(self) -> str:
        """Get tool name from schema."""
        return self.schema.name

    @property
    def version(self) -> str:
        """Get tool version from schema."""
        return self.schema.version

    def validate_parameters(self, parameters: Dict[str, Any]) -> None:
        """
        Validate parameters against schema.

        Args:
            parameters: Parameters to validate

        Raises:
            ValueError: If validation fails
        """
        required_params = [
            param.name for param in self.schema.parameters if param.required
        ]

        missing = set(required_params) - set(parameters.keys())
        if missing:
            raise ValueError(f"Missing required parameters: {', '.join(missing)}")

        logger.debug(f"Parameters validated for tool: {self.name}")

    async def run(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the tool with validation.

        Args:
            parameters: Tool execution parameters

        Returns:
            Dict[str, Any]: Execution result
        """
        logger.info(f"Running tool: {self.name}")

        self.validate_parameters(parameters)

        result = await self.execute(parameters)

        logger.info(f"Tool {self.name} completed successfully")
        return result

    def __repr__(self) -> str:
        return f"<Tool: {self.name} v{self.version}>"
