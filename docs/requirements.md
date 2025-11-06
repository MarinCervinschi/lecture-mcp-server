# Project Requirements

## Core Concept
**MCP Server** using the official **Python MCP SDK** that processes lecture materials from PDFs into clean, structured content. Focus on tool implementation and business logic while leveraging the standard MCP protocol implementation.

## Functional Requirements

### PDF Processing & Chunking
- [x] PDF text extraction with basic structure detection
- [x] Intelligent chunking for large documents
- [x] Context-aware splitting (page boundaries, sections)
- [x] Chunk size optimization for LLM context windows

### Gemini API Integration
- [x] Structured prompts for Markdown conversion
- [x] Content filtering and cleaning via LLM
- [x] LaTeX formula preservation through LLM processing
- [ ] Batch processing for multi-chunk documents
- [ ] Response aggregation and reconstruction

### MCP Server Implementation (SDK-based)
- [ ] Migration to official `mcp` Python SDK
- [ ] stdio transport for AI agent integration (Claude Desktop, etc.)
- [ ] SSE transport for web-based clients
- [ ] HTTP transport adapter for REST compatibility
- [ ] Standard MCP protocol compliance via SDK

### Tool Implementation Focus
- [x] Tool registry and discovery system
- [x] Base tool abstraction and interface
- [x] Three core tools: pdf_to_text, text_to_markdown, filter_content
- [ ] Advanced PDF processing tools
- [ ] Multi-step processing workflows
- [ ] Tool composition and chaining

## Non-Functional Requirements

### Performance
- [x] Efficient PDF parsing (text only, no complex layout analysis)
- [x] Smart chunking to minimize LLM API calls
- [x] Async processing for concurrent operations
- [ ] Response time optimization through parallel LLM calls

### Reliability
- [x] LLM API rate limit handling
- [x] Retry mechanisms for failed operations
- [x] Input validation for PDF files
- [ ] Partial success handling (some chunks fail)
- [ ] Circuit breaker pattern for external APIs

### MCP Compliance
- [ ] **Official SDK implementation** (replacing custom REST)
- [ ] Standard protocol messages (tools/list, tools/call)
- [ ] Proper error codes and responses
- [ ] Multiple transport support (stdio, SSE, HTTP)
- [ ] SDK lifecycle management

## Development Phases

### ~~Phase 1: Foundation~~ ✅ COMPLETED (v0.1.0)
- [x] FastAPI project structure with custom MCP implementation
- [x] Basic PDF text extraction
- [x] Gemini API client setup
- [x] Tool registry system
- [x] Three working tools
- [x] Custom REST API

### Phase 2: SDK Migration (v0.2.0) 🎯 CURRENT
- [ ] Install and configure `mcp` Python SDK
- [ ] Create MCP server wrapper using SDK
- [ ] Migrate tool discovery to SDK format
- [ ] Migrate tool execution to SDK handlers
- [ ] Add stdio transport for AI agents
- [ ] Add SSE transport for web clients
- [ ] Add HTTP adapter for REST compatibility
- [ ] Remove custom FastAPI MCP endpoints
- [ ] Update documentation for SDK usage

### Phase 3: Advanced Tools (v0.3.0)
- [ ] Multi-page PDF processing with progress tracking
- [ ] Batch processing for multiple documents
- [ ] Tool composition (chain pdf_to_text → text_to_markdown → filter_content)
- [ ] Advanced chunking strategies
- [ ] Result caching and optimization

### Phase 4: Production Features (v0.4.0)
- [ ] Resource management (prompts, templates)
- [ ] Sampling support for testing
- [ ] WebSocket transport for real-time updates
- [ ] Monitoring and metrics
- [ ] Docker deployment
- [ ] Performance optimization

## Learning Objectives

### Primary Goals (Updated)
1. **MCP Protocol Mastery**: Understand protocol through SDK usage
2. **Tool Development**: Build complex, composable MCP tools
3. **Async Programming**: Implement efficient concurrent operations
4. **LLM Orchestration**: Manage complex document processing workflows

### Secondary Goals
- SDK integration patterns
- Transport layer understanding (stdio, SSE, WebSocket)
- Prompt engineering optimization
- Production deployment of MCP servers

## Key Technical Decisions

### ✅ Decided in v0.1.0
1. **Chunking Strategy**: Page-based chunking with configurable overlap
2. **Tool Architecture**: Registry-based system with base abstraction
3. **API Framework**: FastAPI for custom REST (to be migrated)

### 🎯 To Decide in v0.2.0
1. **Transport Priority**: stdio first (for Claude Desktop), then SSE/HTTP
2. **Migration Strategy**: Complete replacement vs. gradual transition
   - **Decision**: Complete replacement, remove custom REST endpoints
3. **Backward Compatibility**: Keep REST API for debugging?
   - **Decision**: No hybrid approach, full SDK migration
4. **Deployment Model**: Standalone stdio server vs. embedded in other apps

### 📋 Future Decisions (v0.3.0+)
1. **Tool Composition**: How to chain multiple tools efficiently
2. **State Management**: Handling multi-step workflows
3. **Caching Strategy**: When to cache LLM responses
4. **Error Recovery**: Retry strategies for complex workflows

## Migration Checklist (v0.1.0 → v0.2.0)

### Remove
- [ ] `app/api/mcp.py` - Custom REST endpoints
- [ ] Custom protocol models in `app/models/mcp.py` (replace with SDK types)
- [ ] Manual schema conversion logic

### Add
- [ ] `app/mcp_server.py` - SDK-based server implementation
- [ ] `mcp` dependency in `pyproject.toml`
- [ ] Transport configuration (stdio, SSE)
- [ ] SDK initialization and lifecycle

### Keep (No Changes)
- [x] `app/mcp_tools` - All tool implementations
- [x] `app/services/mcp_registry.py` - Tool registry (minor interface updates)
- [x] `app/utils` - Chunker, Gemini client, etc.
- [x] `app/core` - Configuration and settings
- [x] Tests for tool logic

### Update
- [ ] `run.py` - Change from FastAPI to MCP server startup
- [ ] Tool registry interface - Adapt to SDK requirements
- [ ] Documentation - SDK usage instead of REST API
- [ ] README - New installation and usage instructions
