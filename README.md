# Lecture MCP Server

A FastAPI-based MCP (Model Context Protocol) server for intelligent processing of lecture materials. Transforms PDF slides and transcriptions into clean, structured content with AI-powered filtering.

## 🚀 Features

- **PDF to Markdown Conversion**: Extract and structure content from lecture PDFs
- **LaTeX Formula Preservation**: Maintain mathematical expressions in clean format
- **AI-Powered Content Filtering**: Remove irrelevant content using Gemini API
- **MCP Protocol Compliance**: Standardized tooling for AI applications
- **RESTful API**: Well-documented endpoints for integration

## 🛠 Tech Stack

- **Framework**: FastAPI
- **MCP**: Model Context Protocol
- **LLM**: Google Gemini API
- **PDF Processing**: PyPDF2 / pdfplumber
- **Package Manager**: uv (fast Python package installer)
- **Python**: 3.12+

## 📋 Prerequisites

- Python 3.12+
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Google Gemini API key

## 🔧 Installation

### 1. Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```

### 2. Clone and Setup

```bash
# Clone repository
git clone https://github.com/yourusername/lecture-mcp-server
cd lecture-mcp-server

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate     # Windows
```

### 3. Configuration

Create a `.env` file:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
GEMINI_API_KEY=your_api_key_here
```

Visit the [app/core/config.py](app/core/config.py) file to adjust other settings as needed.

## 🚀 Usage

### Starting the Server

```bash
# With uv (recommended)
uv run python run.py

# Or python directly (if virtual environment is activated)
python run.py
```

### API Documentation

Visit the interactive API documentation:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/api/health

## 📚 API Endpoints

### Health Check
```bash
GET /api/health
```

### MCP Tools (Coming Soon)
- `POST /api/mcp/tools/pdf-to-markdown` - Convert PDF to structured Markdown
- `POST /api/mcp/tools/filter-content` - AI-powered content filtering
- `GET /api/mcp/tools` - List available MCP tools

## 🧪 Testing

```bash
# Run tests
uv run pytest

# Run with coverage
uv run pytest --cov=app --cov-report=html

# Run specific test file
uv run pytest tests/test_health.py
```

## 🔨 Development

### Adding Dependencies

```bash
# Add production dependency
uv add package-name

# Add development dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade
```

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

## 🐳 Docker (Coming Soon)


## 📖 Documentation

- [Project Requirements](requirements.md)
- [Task Breakdown](tasks.md)
- [API Documentation](http://localhost:8000/docs) (when server is running)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details