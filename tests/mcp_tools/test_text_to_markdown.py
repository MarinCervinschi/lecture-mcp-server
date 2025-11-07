from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.gemini_client import GeminiAPIError, GeminiResponse
from app.tools.text_to_markdown import (
    TextToMarkdownArgs,
    TextToMarkdownResult,
    TextToMarkdownTool,
)


class TestTextToMarkdownTool:
    """Test suite for TextToMarkdownTool."""

    @pytest.fixture
    def text_to_markdown_tool(self) -> TextToMarkdownTool:
        """Create TextToMarkdownTool instance with mocked Gemini client."""
        with patch("app.tools.text_to_markdown.get_gemini_client"):
            tool = TextToMarkdownTool()
            tool.gemini_client = MagicMock()
            return tool

    @pytest.fixture
    def sample_text(self) -> str:
        """Sample plain text for testing."""
        return """
        Introduction to Python
        Python is a high-level programming language
        
        Variables and Types
        x = 5
        Formula: f(x) = x^2 + 2x + 1
        """

    @pytest.fixture
    def expected_markdown(self) -> str:
        """Expected markdown output."""
        return """# Introduction to Python

Python is a high-level programming language

## Variables and Types

```python
x = 5
```

Formula: $f(x) = x^2 + 2x + 1$"""

    def test_schema_properties(self, text_to_markdown_tool: TextToMarkdownTool):
        """Test tool schema has correct properties."""
        schema = text_to_markdown_tool.schema

        assert schema.name == "text_to_markdown"
        assert schema.description is not None
        assert "inputSchema" in schema.model_dump()
        assert "outputSchema" in schema.model_dump()

        # Verify inputSchema has content field
        input_schema = schema.inputSchema
        assert "properties" in input_schema
        assert "content" in input_schema["properties"]
        assert input_schema["required"] == ["content"]

    def test_args_validation(self):
        """Test TextToMarkdownArgs validation."""
        # Valid args
        args = TextToMarkdownArgs(content="Test content")
        assert args.content == "Test content"

        # Invalid - empty string
        with pytest.raises(ValueError):
            TextToMarkdownArgs(content="")

        # Invalid - None
        with pytest.raises(ValueError):
            TextToMarkdownArgs(content=None)  # type: ignore

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        text_to_markdown_tool: TextToMarkdownTool,
        sample_text: str,
        expected_markdown: str,
    ):
        """Test successful markdown conversion."""
        # Mock Gemini response
        mock_response = GeminiResponse(
            content=expected_markdown,
            model="gemini-2.0-flash",
            prompt_tokens=100,
            completion_tokens=150,
            total_tokens=250,
            finish_reason="STOP",
        )

        text_to_markdown_tool.gemini_client.generate_with_retry = AsyncMock(
            return_value=mock_response
        )

        # Execute
        parameters = {"content": sample_text}
        result = await text_to_markdown_tool.execute(parameters)

        # Verify result structure
        assert "markdown" in result
        assert result["markdown"] == expected_markdown

        # Verify Gemini client was called
        text_to_markdown_tool.gemini_client.generate_with_retry.assert_called_once()
        call_args = (
            text_to_markdown_tool.gemini_client.generate_with_retry.call_args.kwargs
        )
        assert "prompt" in call_args
        assert sample_text in call_args["prompt"]
        assert call_args["temperature"] == 0.3
        assert call_args["max_tokens"] == 8000

    @pytest.mark.asyncio
    async def test_execute_with_latex(self, text_to_markdown_tool: TextToMarkdownTool):
        """Test conversion of text with LaTeX formulas."""
        input_text = "The quadratic formula is x = (-b ± sqrt(b^2 - 4ac)) / 2a"
        expected_output = (
            "The quadratic formula is $x = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$"
        )

        mock_response = GeminiResponse(
            content=expected_output,
            model="gemini-2.0-flash",
            prompt_tokens=50,
            completion_tokens=60,
            total_tokens=110,
            finish_reason="STOP",
        )

        text_to_markdown_tool.gemini_client.generate_with_retry = AsyncMock(
            return_value=mock_response
        )

        parameters = {"content": input_text}
        result = await text_to_markdown_tool.execute(parameters)

        assert result["markdown"] == expected_output

    @pytest.mark.asyncio
    async def test_execute_gemini_api_error(
        self, text_to_markdown_tool: TextToMarkdownTool
    ):
        """Test handling of Gemini API errors."""
        text_to_markdown_tool.gemini_client.generate_with_retry = AsyncMock(
            side_effect=GeminiAPIError("API quota exceeded")
        )

        parameters = {"content": "Test content"}

        with pytest.raises(GeminiAPIError) as exc_info:
            await text_to_markdown_tool.execute(parameters)

        assert "API quota exceeded" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_invalid_parameters(
        self, text_to_markdown_tool: TextToMarkdownTool
    ):
        """Test execution with invalid parameters."""
        # Missing content
        with pytest.raises(ValueError):
            await text_to_markdown_tool.execute({})

        # Empty content
        with pytest.raises(ValueError):
            await text_to_markdown_tool.execute({"content": ""})

    @pytest.mark.asyncio
    async def test_execute_strips_whitespace(
        self, text_to_markdown_tool: TextToMarkdownTool
    ):
        """Test that output is stripped of excess whitespace."""
        mock_response = GeminiResponse(
            content="  \n\n# Title\n\nContent\n\n  ",
            model="gemini-2.0-flash",
            prompt_tokens=50,
            completion_tokens=60,
            total_tokens=110,
            finish_reason="STOP",
        )

        text_to_markdown_tool.gemini_client.generate_with_retry = AsyncMock(
            return_value=mock_response
        )

        parameters = {"content": "Test content"}
        result = await text_to_markdown_tool.execute(parameters)

        assert result["markdown"] == "# Title\n\nContent"
        assert not result["markdown"].startswith(" ")
        assert not result["markdown"].endswith(" ")

    @pytest.mark.asyncio
    async def test_result_model_validation(
        self, text_to_markdown_tool: TextToMarkdownTool
    ):
        """Test TextToMarkdownResult model validation."""
        # Valid result
        result = TextToMarkdownResult(markdown="# Test")
        assert result.markdown == "# Test"

        # Convert to dict
        result_dict = result.model_dump()
        assert "markdown" in result_dict
        assert result_dict["markdown"] == "# Test"

    def test_prompt_loading(self, text_to_markdown_tool: TextToMarkdownTool):
        """Test that prompt is loaded correctly."""
        assert text_to_markdown_tool.prompt is not None
        assert len(text_to_markdown_tool.prompt) > 0
        assert "{content}" in text_to_markdown_tool.prompt
