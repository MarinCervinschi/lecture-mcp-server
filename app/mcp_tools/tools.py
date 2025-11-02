from app.models.mcp import ToolSchema
from typing import List
from app.mcp_tools.text_to_markdown import create_text_to_markdown_tool
from app.mcp_tools.filter_content import create_filter_content_tool
from app.mcp_tools.pdf_to_text import create_pdf_to_text_tool


def get_all_tools() -> List[ToolSchema]:
    """
    Get all available MCP tools.

    Returns:
        List[ToolSchema]: List of all tool definitions
    """
    return [
        create_text_to_markdown_tool(),
        create_filter_content_tool(),
        create_pdf_to_text_tool(),
    ]
