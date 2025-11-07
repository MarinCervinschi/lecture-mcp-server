# Lecture MCP Server

A general-purpose MCP (Model Context Protocol) server for processing lecture materials from PDFs. Extracts text, chunks it for LLM processing, and converts to clean Markdown with LaTeX support using Google Gemini AI.

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-1.21.0-orange?style=for-the-badge&logo=protocol&logoColor=white" alt="MCP"></a>
  <a href="https://ai.google.dev/"><img src="https://img.shields.io/badge/Google_Gemini-AI-4285F4?style=for-the-badge&logo=google&logoColor=white" alt="Google Gemini"></a>
  <a href="https://developers.google.com/adk"><img src="https://img.shields.io/badge/Google_ADK-Agent_Dev_Kit-34A853?style=for-the-badge&logo=google&logoColor=white" alt="Google ADK"></a>
  <a href="https://github.com/astral-sh/uv"><img src="https://img.shields.io/badge/uv-package_manager-purple?style=for-the-badge&logo=astral&logoColor=white" alt="uv"></a>
  <a href="https://www.uvicorn.org/"><img src="https://img.shields.io/badge/Uvicorn-SSE-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="Uvicorn"></a>

</p>

## 🚀 Features

- **PDF Text Extraction**: Extract and chunk text from PDF files optimized for LLM context limits
- **Markdown Conversion**: Transform plain text into well-formatted Markdown with LaTeX support
- **MCP Protocol**: Supports SSE (Server-Sent Events) and stdio transports
- **AI-Powered**: Uses Google Gemini for intelligent content formatting
- **Extensible**: Easy to add custom tools to the registry

## 📋 Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Google Gemini API key ([Get one here](https://aistudio.google.com/apikey))

## 🔧 Installation

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/MarinCervinschi/lecture-mcp-server
cd lecture-mcp-server

# Install dependencies
uv sync
```

### 3. Configure API Key

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

## 🚀 Usage

### Running the Server

#### SSE Transport (Recommended)

```bash
uv run python run.py --transport sse
```

The server will start on `http://localhost:8000/mcp`

This is the recommended transport method for testing and integration with MCP clients.

#### Stdio Transport

```bash
uv run python run.py --transport stdio
```

> ⚠️ **Note**: The stdio transport method is not fully tested yet.

### Testing the Server

#### 1. Start the SSE Server ⬆️

#### 2. Test with Google ADK Web UI

In a separate terminal, start the ADK web interface:

```bash
adk web --port 8080
```

Then open your browser at `http://localhost:8080` to interact with the agent that uses the MCP server tools.

The example agent configuration is in `sse_agent/agent.py` - this is just a testing tool to verify the MCP server works correctly.

## ⚙️ Available MCP Tools

### 1. `pdf_to_text`

Extract text from PDF and chunk for LLM processing.

**Input:**

- `file_data` (string): Base64 encoded PDF file content

**Output:**

- `metadata`: PDF information (pages, size, etc.)
- `total_chunks`: Number of chunks created
- `chunks`: List of text chunks with page numbers and token counts

### 2. `text_to_markdown`

Convert plain text to well-formatted Markdown with LaTeX support.

**Input:**

- `content` (string): Plain text to convert

**Output:**

- `markdown`: Formatted Markdown content

### 3. `filter_content`

Filter and clean up content by removing noise and irrelevant information.

**Input:**

- `content` (string): Text to filter

**Output:**

- `filtered_content`: Cleaned and filtered text

## 🧪 Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test
uv run pytest tests/mcp_tools/test_pdf_to_text.py
```

## 🔨 Development

### Adding a New Tool

To add a custom tool to the MCP server:

#### 1. Create the Tool Class

Create a new file in [app/tools/](app/tools/) (e.g., `my_new_tool.py`):

```python
from typing import Any, Dict
from mcp.types import Tool as MCPTool
from pydantic import BaseModel, Field
from app.tools.base import BaseMCPTool

class MyToolArgs(BaseModel):
    """Input schema for the tool"""
    input_param: str = Field(..., description="Description of the parameter")

class MyToolResult(BaseModel):
    """Output schema for the tool"""
    result: str = Field(..., description="Description of the result")

class MyNewTool(BaseMCPTool):
    """Description of what your tool does."""

    def _create_schema(self) -> MCPTool:
        """Create tool schema for MCP."""
        return MCPTool(
            name="my_new_tool",
            description="What this tool does",
            inputSchema=MyToolArgs.model_json_schema(),
            outputSchema=MyToolResult.model_json_schema(),
        )

    async def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the tool logic."""
        validated_params = MyToolArgs(**args)

        # Your tool logic here
        result = MyToolResult(result=f"Processed: {validated_params.input_param}")

        return result.model_dump()
```

#### 2. Register the Tool

Open [app/services/mcp_registry.py](app/services/mcp_registry.py) and add your tool:

```python
from app.tools.my_new_tool import MyNewTool

class MCPToolRegistry:
    def _register_default_tools(self) -> None:
        """Register all default tools."""
        tools: List[Tool] = [
            PDFToTextTool(),
            TextToMarkdownTool(),
            MyNewTool(),  # Add your tool here
        ]
```

#### 3. Test Your Tool

Restart the server and your tool will be automatically available through the MCP protocol.

### Adding Dependencies

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev package-name
```

### Configuration

All settings are in [app/core/config.py](app/core/config.py). Key settings:

- `GEMINI_MODEL`: Model to use (default: gemini-2.5-flash)
- `MAX_CHUNK_SIZE`: Token limit per chunk (default: 2000)
- `MAX_FILE_SIZE`: Max PDF size in bytes (default: 10MB)
- `HOST`/`PORT`: Server host and port (default: 0.0.0.0:8000)

### Code Quality

```bash
# Format code
uv run black app/
uv run isort app/

# Lint
uv run ruff check app/

# Type checking
uv run mypy app/
```

## 📖 Additional Documentation

- [Project Requirements](docs/requirements.md)
- [Task Breakdown](docs/tasks.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and code quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details
