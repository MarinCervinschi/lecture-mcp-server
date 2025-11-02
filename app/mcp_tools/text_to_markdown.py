from app.models.mcp import ToolSchema, ToolParameter, ToolParameterType

def create_text_to_markdown_tool() -> ToolSchema:
    """
    Create text to Markdown conversion tool schema.

    Returns:
        ToolSchema: Tool definition for text to Markdown conversion
    """
    return ToolSchema(
        name="text_to_markdown",
        description="Convert plain text to well-formatted Markdown with LaTeX support",
        version="1.0.0",
        parameters=[
            ToolParameter(
                name="content",
                type=ToolParameterType.STRING,
                description="Text content to convert to Markdown",
                required=True,
            ),
        ],
    )
