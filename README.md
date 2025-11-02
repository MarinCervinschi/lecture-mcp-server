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
- **Async Support**: Python 3.8+
- **Container**: Docker

## 📋 Prerequisites

- Python 3.8+
- Google Gemini API key
- Poetry or pip for dependency management

## 🔧 Installation

```bash
git clone https://github.com/yourusername/lecture-mcp-server
cd lecture-mcp-server
poetry install
```

## ⚙️ Configuration

Set your environment variables:
```bash
export GEMINI_API_KEY=your_key_here
export MCP_SERVER_PORT=8000
```

## 🚀 Usage

### Starting the Server
```bash
uvicorn main:app --reload --port 8000
```

### API Documentation
Visit `http://localhost:8000/docs` for interactive API docs.

## 📚 API Endpoints

- `POST /mcp/tools/pdf-to-markdown` - Convert PDF to structured Markdown
- `POST /mcp/tools/filter-content` - AI-powered content filtering
- `GET /mcp/tools` - List available MCP tools

## 🏗 Project Structure

```
lecture-mcp-server/
├── app/
│   ├── core/          # Configuration and base classes
│   ├── mcp/           # MCP protocol implementation
│   ├── services/      # Business logic (PDF, LLM services)
│   ├── models/        # Pydantic models
│   └── api/           # FastAPI routes
├── tests/
├── docs/
└── scripts/
```

## 🧪 Testing

```bash
pytest tests/
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details