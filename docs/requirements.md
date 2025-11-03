# Project Requirements

## Core Concept
**FastAPI MCP Server** that acts as a bridge between PDF documents and Gemini AI API, focusing on MCP protocol implementation and intelligent API orchestration.

## Functional Requirements

### PDF Processing & Chunking
- [ ] PDF text extraction with basic structure detection
- [ ] Intelligent chunking for large documents
- [ ] Context-aware splitting (page boundaries, sections)
- [ ] Chunk size optimization for LLM context windows

### Gemini API Integration
- [ ] Structured prompts for Markdown conversion
- [ ] Content filtering and cleaning via LLM
- [ ] LaTeX formula preservation through LLM processing
- [ ] Batch processing for multi-chunk documents
- [ ] Response aggregation and reconstruction

### MCP Server Implementation
- [ ] MCP protocol compliance and tool definitions
- [ ] Tool discovery endpoint
- [ ] Standardized error handling per MCP spec
- [ ] Resource management interface

### API Orchestration
- [ ] Document upload and processing queue
- [ ] Async processing with progress tracking
- [ ] Chunk management and sequencing
- [ ] Result aggregation from multiple LLM calls

## Non-Functional Requirements

### Performance
- [ ] Efficient PDF parsing (text only, no complex layout analysis)
- [ ] Smart chunking to minimize LLM API calls
- [ ] Async processing for concurrent operations
- [ ] Response time optimization through parallel LLM calls

### Reliability
- [ ] LLM API rate limit handling
- [ ] Retry mechanisms for failed chunks
- [ ] Partial success handling (some chunks fail)
- [ ] Input validation for PDF files

### MCP Compliance
- [ ] Proper tool schema definitions
- [ ] Standardized error responses
- [ ] Resource cleanup
- [ ] Protocol version handling

## Technical Implementation Focus

### PDF Processing (Lightweight)
- Use `PyPDF2` or `pdfplumber` for text extraction
- Focus on page-level chunking
- Preserve basic structure (headings detection via simple heuristics)

### Gemini API Integration
- Design focused prompts for:
  - Markdown conversion with structure
  - Content filtering (remove jokes, anecdotes, off-topic)
  - LaTeX preservation
- Handle token limits through chunking
- Maintain conversation context across chunks if needed

### MCP Tool Design
```python
# Example tool definitions
tools = [
    {
        "name": "pdf_to_structured_markdown",
        "description": "Convert PDF lecture materials to clean Markdown with LaTeX",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string"},
                "chunk_size": {"type": "integer", "default": 2000}
            }
        }
    },
    {
        "name": "filter_lecture_content", 
        "description": "Remove non-essential content from lecture transcriptions",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string"},
                "filter_level": {"type": "string", "enum": ["aggressive", "moderate"]}
            }
        }
    }
]
```

## Development Phases

### Phase 1: Foundation
- FastAPI project structure with MCP skeleton
- Basic PDF text extraction
- Gemini API client setup
- Simple single-chunk processing

### Phase 2: Chunking & Orchestration
- Document chunking logic
- Batch LLM API calls
- Result aggregation
- Progress tracking

### Phase 3: MCP Protocol
- Tool definitions and discovery
- MCP-compliant error handling
- Resource management
- Protocol testing

### Phase 4: Optimization
- Prompt engineering refinement
- Chunking strategy optimization
- Error handling and retry logic
- Performance testing

## Learning Objectives

### Primary Goals
1. **MCP Protocol Mastery**: Understand and implement MCP server specifications
2. **FastAPI Best Practices**: Build production-ready REST APIs with proper structure
3. **LLM API Orchestration**: Manage complex document processing through external AI services
4. **Async Programming**: Implement efficient concurrent operations

### Secondary Goals
- PDF processing basics
- Prompt engineering patterns
- Error handling in distributed systems
- API design for AI applications

## Key Technical Decisions

1. **Chunking Strategy**: Page-based vs. content-based chunking
2. **LLM Context Management**: How to maintain coherence across chunks
3. **Error Handling**: Partial failure strategies for multi-chunk documents
4. **MCP Tool Granularity**: Fine-grained vs. coarse-grained tools
