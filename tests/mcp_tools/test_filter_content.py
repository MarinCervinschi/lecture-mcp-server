from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.gemini_client import GeminiAPIError, GeminiResponse
from app.tools.filter_content import (
    FilterContentArgs,
    FilterContentResult,
    FilterContentTool,
)


class TestFilterContentTool:
    """Test suite for FilterContentTool."""

    @pytest.fixture
    def filter_content_tool(self) -> FilterContentTool:
        """Create FilterContentTool instance with mocked Gemini client."""
        with patch("app.tools.filter_content.get_gemini_client"):
            tool = FilterContentTool()
            tool.gemini_client = MagicMock()
            return tool

    @pytest.fixture
    def noisy_text(self) -> str:
        """Sample text with noise and irrelevant content."""
        return """
        Page 1 of 10
        
        Introduction to Machine Learning
        
        This is important content about ML algorithms.
        
        Next slide >
        
        Linear Regression
        The formula is: y = mx + b
        
        << Previous | Home | Next >>
        
        Copyright © 2024. All rights reserved.
        Page 2 of 10
        """

    @pytest.fixture
    def clean_text(self) -> str:
        """Expected clean output."""
        return """Introduction to Machine Learning

This is important content about ML algorithms.

Linear Regression
The formula is: y = mx + b"""

    def test_schema_properties(self, filter_content_tool: FilterContentTool):
        """Test tool schema has correct properties."""
        schema = filter_content_tool.schema

        assert schema.name == "filter_content"
        assert schema.description is not None
        assert "inputSchema" in schema.model_dump()
        assert "outputSchema" in schema.model_dump()

        # Verify inputSchema has content field
        input_schema = schema.inputSchema
        assert "properties" in input_schema
        assert "content" in input_schema["properties"]
        assert input_schema["required"] == ["content"]

    def test_args_validation(self):
        """Test FilterContentArgs validation."""
        # Valid args
        args = FilterContentArgs(content="Test content with noise")
        assert args.content == "Test content with noise"

        # Invalid - empty string
        with pytest.raises(ValueError):
            FilterContentArgs(content="")

        # Invalid - None
        with pytest.raises(ValueError):
            FilterContentArgs(content=None)  # type: ignore

    @pytest.mark.asyncio
    async def test_execute_success(
        self,
        filter_content_tool: FilterContentTool,
        noisy_text: str,
        clean_text: str,
    ):
        """Test successful content filtering."""
        # Mock Gemini response
        mock_response = GeminiResponse(
            content=clean_text,
            model="gemini-2.0-flash",
            prompt_tokens=100,
            completion_tokens=80,
            total_tokens=180,
            finish_reason="STOP",
        )

        filter_content_tool.gemini_client.generate_with_retry = AsyncMock(
            return_value=mock_response
        )

        # Execute
        parameters = {"content": noisy_text}
        result = await filter_content_tool.execute(parameters)

        # Verify result structure
        assert "filtered_content" in result
        assert result["filtered_content"] == clean_text

        # Verify Gemini client was called
        filter_content_tool.gemini_client.generate_with_retry.assert_called_once()
        call_args = (
            filter_content_tool.gemini_client.generate_with_retry.call_args.kwargs
        )
        assert "prompt" in call_args
        assert noisy_text in call_args["prompt"]
        assert call_args["temperature"] == 0.3
        assert call_args["max_tokens"] == 8000

    @pytest.mark.asyncio
    async def test_execute_removes_navigation(
        self, filter_content_tool: FilterContentTool
    ):
        """Test that navigation elements are removed."""
        input_text = """
        Main Content Here
        << Previous | Next >>
        More content
        Back to top
        """
        expected_output = "Main Content Here\nMore content"

        mock_response = GeminiResponse(
            content=expected_output,
            model="gemini-2.0-flash",
            prompt_tokens=50,
            completion_tokens=40,
            total_tokens=90,
            finish_reason="STOP",
        )

        filter_content_tool.gemini_client.generate_with_retry = AsyncMock(
            return_value=mock_response
        )

        parameters = {"content": input_text}
        result = await filter_content_tool.execute(parameters)

        assert "filtered_content" in result
        # Verify navigation elements are not in output
        assert "Previous" not in result["filtered_content"]
        assert "Next" not in result["filtered_content"]
        assert "Back to top" not in result["filtered_content"]

    @pytest.mark.asyncio
    async def test_execute_preserves_formulas(
        self, filter_content_tool: FilterContentTool
    ):
        """Test that formulas and code blocks are preserved."""
        input_text = """
        Page 1 of 5
        
        The equation is: $$E = mc^2$$
        
        Code example:
        ```python
        print("hello")
        ```
        
        << Back
        """
        expected_output = """The equation is: $$E = mc^2$$

Code example:
```python
print("hello")
```"""

        mock_response = GeminiResponse(
            content=expected_output,
            model="gemini-2.0-flash",
            prompt_tokens=80,
            completion_tokens=60,
            total_tokens=140,
            finish_reason="STOP",
        )

        filter_content_tool.gemini_client.generate_with_retry = AsyncMock(
            return_value=mock_response
        )

        parameters = {"content": input_text}
        result = await filter_content_tool.execute(parameters)

        # Verify formulas and code are preserved
        assert "$$E = mc^2$$" in result["filtered_content"]
        assert "```python" in result["filtered_content"]
        assert 'print("hello")' in result["filtered_content"]

    @pytest.mark.asyncio
    async def test_execute_gemini_api_error(
        self, filter_content_tool: FilterContentTool
    ):
        """Test handling of Gemini API errors."""
        filter_content_tool.gemini_client.generate_with_retry = AsyncMock(
            side_effect=GeminiAPIError("Connection timeout")
        )

        parameters = {"content": "Test content"}

        with pytest.raises(GeminiAPIError) as exc_info:
            await filter_content_tool.execute(parameters)

        assert "Connection timeout" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_execute_invalid_parameters(
        self, filter_content_tool: FilterContentTool
    ):
        """Test execution with invalid parameters."""
        # Missing content
        with pytest.raises(ValueError):
            await filter_content_tool.execute({})

        # Empty content
        with pytest.raises(ValueError):
            await filter_content_tool.execute({"content": ""})

    @pytest.mark.asyncio
    async def test_execute_strips_whitespace(
        self, filter_content_tool: FilterContentTool
    ):
        """Test that output is stripped of excess whitespace."""
        mock_response = GeminiResponse(
            content="  \n\nClean content here\n\n  ",
            model="gemini-2.0-flash",
            prompt_tokens=50,
            completion_tokens=40,
            total_tokens=90,
            finish_reason="STOP",
        )

        filter_content_tool.gemini_client.generate_with_retry = AsyncMock(
            return_value=mock_response
        )

        parameters = {"content": "Noisy content"}
        result = await filter_content_tool.execute(parameters)

        assert result["filtered_content"] == "Clean content here"
        assert not result["filtered_content"].startswith(" ")
        assert not result["filtered_content"].endswith(" ")

    @pytest.mark.asyncio
    async def test_result_model_validation(
        self, filter_content_tool: FilterContentTool
    ):
        """Test FilterContentResult model validation."""
        # Valid result
        result = FilterContentResult(filtered_content="Clean text")
        assert result.filtered_content == "Clean text"

        # Convert to dict
        result_dict = result.model_dump()
        assert "filtered_content" in result_dict
        assert result_dict["filtered_content"] == "Clean text"

    def test_prompt_loading(self, filter_content_tool: FilterContentTool):
        """Test that prompt is loaded correctly."""
        assert filter_content_tool.prompt is not None
        assert len(filter_content_tool.prompt) > 0
        assert "{content}" in filter_content_tool.prompt

    @pytest.mark.asyncio
    async def test_execute_with_large_content(
        self, filter_content_tool: FilterContentTool
    ):
        """Test filtering of large content."""
        large_content = "Line of text.\n" * 1000
        filtered = "Filtered content"

        mock_response = GeminiResponse(
            content=filtered,
            model="gemini-2.0-flash",
            prompt_tokens=5000,
            completion_tokens=100,
            total_tokens=5100,
            finish_reason="STOP",
        )

        filter_content_tool.gemini_client.generate_with_retry = AsyncMock(
            return_value=mock_response
        )

        parameters = {"content": large_content}
        result = await filter_content_tool.execute(parameters)

        assert result["filtered_content"] == filtered
        # Verify call was made with large content
        call_args = (
            filter_content_tool.gemini_client.generate_with_retry.call_args.kwargs
        )
        assert len(call_args["prompt"]) > 10000
