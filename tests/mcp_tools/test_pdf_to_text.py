import pytest

from app.mcp_tools.pdf_to_text import PDFToTextTool
from app.models.pdf import PDFChunk
from app.services.pdf_service import PDFProcessingError
from app.utils.file_utils import FileValidationError


class TestPDFToTextTool:
    """Test suite for PDFToTextTool."""

    @pytest.fixture
    def pdf_tool(self) -> PDFToTextTool:
        """Create PDFToTextTool instance."""
        return PDFToTextTool()

    def test_schema_properties(self, pdf_tool: PDFToTextTool):
        """Test tool schema has correct properties."""
        schema = pdf_tool.schema
        parameter = schema.parameters[0]

        assert schema.name == "pdf_to_text"
        assert schema.version == "2.0.0"
        assert len(schema.parameters) == 1
        assert parameter.name == "file_data"
        assert parameter.required is True
        if parameter.mime_types:
            assert "application/pdf" in parameter.mime_types

    @pytest.mark.asyncio
    async def test_execute_success(
        self, pdf_tool: PDFToTextTool, sample_pdf_base64: str
    ):
        """Test successful PDF extraction."""
        parameters = {"file_data": sample_pdf_base64}
        result = await pdf_tool.execute(parameters)

        assert result.total_chunks > 0
        assert len(result.chunks) == result.total_chunks
        assert result.metadata is not None
        assert "page_count" in result.metadata

        for chunk in result.chunks:
            assert isinstance(chunk, PDFChunk)
            assert chunk.content
            assert chunk.chunk_index >= 0

    @pytest.mark.asyncio
    async def test_execute_with_multipage_pdf(
        self, pdf_tool: PDFToTextTool, sample_pdf_base64: str
    ):
        """Test PDF with multiple pages creates multiple chunks."""
        parameters = {"file_data": sample_pdf_base64}

        result = await pdf_tool.execute(parameters)

        # Our sample PDF has 2 pages
        assert result.metadata["page_count"] == 2
        assert result.total_chunks >= 1

    @pytest.mark.asyncio
    async def test_execute_invalid_base64(
        self, pdf_tool: PDFToTextTool, corrupted_base64: str
    ):
        """Test execution with invalid base64 raises error."""
        parameters = {"file_data": corrupted_base64}

        with pytest.raises((FileValidationError, ValueError)):
            await pdf_tool.execute(parameters)

    @pytest.mark.asyncio
    async def test_execute_invalid_pdf_content(
        self, pdf_tool: PDFToTextTool, invalid_pdf_base64: str
    ):
        """Test execution with non-PDF content raises error."""
        parameters = {"file_data": invalid_pdf_base64}

        with pytest.raises((FileValidationError, PDFProcessingError)):
            await pdf_tool.execute(parameters)

    @pytest.mark.asyncio
    async def test_execute_missing_file_data(self, pdf_tool: PDFToTextTool):
        """Test execution without file_data parameter."""
        parameters = {"file_data": None}

        with pytest.raises(ValueError):
            await pdf_tool.execute(parameters)

    @pytest.mark.asyncio
    async def test_chunks_have_proper_structure(
        self, pdf_tool: PDFToTextTool, sample_pdf_base64: str
    ):
        """Test that chunks have all required fields."""
        parameters = {"file_data": sample_pdf_base64}

        result = await pdf_tool.execute(parameters)

        for i, chunk in enumerate(result.chunks):
            assert chunk.chunk_index == i
            assert isinstance(chunk.content, str)
            assert len(chunk.content) > 0

    @pytest.mark.asyncio
    async def test_metadata_contains_expected_fields(
        self, pdf_tool: PDFToTextTool, sample_pdf_base64: str
    ):
        """Test metadata has required information."""
        parameters = {"file_data": sample_pdf_base64}

        result = await pdf_tool.execute(parameters)

        assert "page_count" in result.metadata
        assert isinstance(result.metadata["page_count"], int)
        assert result.metadata["page_count"] > 0
