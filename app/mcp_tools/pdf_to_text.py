from app.models.mcp import ToolSchema, ToolParameter, ToolParameterType
from app.core.config import settings


def create_pdf_to_text_tool() -> ToolSchema:
    """
    Create PDF to text conversion tool schema.

    Returns:
        ToolSchema: Tool definition for PDF to text conversion
    """
    return ToolSchema(
        name="pdf_to_text",
        description="Convert PDF documents to plain text format",
        version="1.0.0",
        parameters=[
            ToolParameter(
                name="file_data",
                type=ToolParameterType.FILE,
                description="PDF file content (base64 encoded string)",
                required=True,
                mime_types=["application/pdf"],
                max_size=settings.MAX_FILE_SIZE,
            ),
        ],
    )
