from app.models.mcp import ToolSchema, ToolParameter, ToolParameterType


def create_filter_content_tool() -> ToolSchema:
    """
    Create content filtering tool schema.

    Returns:
        ToolSchema: Tool definition for content filtering
    """
    return ToolSchema(
        name="filter_content",
        description="Remove noise from ANY text content (slides, transcripts, documents, etc.)",
        version="1.0.0",
        parameters=[
            ToolParameter(
                name="content",
                type=ToolParameterType.STRING,
                description="Text content to filter",
                required=True,
            ),
        ],
    )
