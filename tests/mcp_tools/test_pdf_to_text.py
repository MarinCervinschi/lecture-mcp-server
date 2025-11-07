import pytest

from app.models.pdf import PDFChunk
from app.services.pdf_service import PDFProcessingError
from app.tools.pdf_to_text import PDFToTextParameters, PDFToTextTool
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

        assert schema.name == "pdf_to_text"
        assert schema.description is not None
        assert "inputSchema" in schema.model_dump()
        assert "outputSchema" in schema.model_dump()

        # Verify inputSchema has file_data field
        input_schema = schema.inputSchema
        assert "properties" in input_schema
        assert "file_data" in input_schema["properties"]
        assert input_schema["required"] == ["file_data"]

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
            assert chunk.token_count > 0
            assert chunk.char_count > 0
            assert chunk.page_range
            assert isinstance(chunk.has_overlap, bool)

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
        with pytest.raises(ValueError):
            PDFToTextParameters(file_data=None)  # type: ignore

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
            assert chunk.token_count > 0
            assert chunk.char_count > 0
            assert isinstance(chunk.page_range, str)
            assert isinstance(chunk.has_overlap, bool)
            if chunk.has_overlap:
                assert chunk.overlap_content is not None

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
