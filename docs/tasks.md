# Project Tasks Breakdown

## ~~Phase 1: Foundation & Basic Setup~~ ✅ COMPLETED (v0.1.0)

### ~~Task 1.1: Project Initialization~~ ✅
- [x] Create Python project structure with uv
- [x] Set up basic FastAPI application with routing
- [x] Configure environment variables and settings management
- [x] Add basic logging and error handling

### ~~Task 1.2: MCP Server Skeleton~~ ✅
- [x] Research MCP specification and requirements
- [x] Create MCP tool discovery endpoint
- [x] Implement basic MCP response format
- [x] Set up MCP error handling structure
- [x] Create MCP tool schema definitions

### ~~Task 1.3: PDF Processing Foundation~~ ✅
- [x] Choose and integrate PDF library (PyPDF2/pdfplumber)
- [x] Create PDF upload endpoint with validation
- [x] Implement basic text extraction from PDF pages
- [x] Handle common PDF extraction errors
- [x] Add file type validation and security checks

### ~~Task 1.4: Gemini API Client~~ ✅
- [x] Create Gemini API client class
- [x] Implement authentication and API key management
- [x] Add basic prompt template structure
- [x] Create error handling for API failures
- [x] Implement rate limiting awareness

## ~~Phase 2: Core Processing & Chunking~~ ✅ COMPLETED (v0.1.0)

### ~~Task 2.1: Document Chunking Strategy~~ ✅
- [x] Analyze different chunking strategies
- [x] Implement page-based chunking as primary approach
- [x] Add chunk size optimization for Gemini context windows
- [x] Create chunk overlap handling for context preservation
- [x] Test chunking with various document types

### ~~Task 2.2: Basic Markdown Conversion~~ ✅
- [x] Design initial prompt for Markdown conversion
- [x] Create service to send chunks to Gemini API
- [x] Implement basic response aggregation
- [x] Handle LaTeX preservation
- [x] Test with simple PDF documents

### ~~Task 2.3: Content Filtering Foundation~~ ✅
- [x] Design prompt for irrelevant content removal
- [x] Create filtering service with configurable levels
- [x] Implement Gemini-based filtering
- [x] Handle different types of irrelevant content
- [x] Test filtering effectiveness

### ~~Task 2.4: Tool Registry System~~ ✅
- [x] Create base tool abstraction
- [x] Implement tool registry with discovery
- [x] Add tool validation and metadata
- [x] Create tool execution pipeline
- [x] Test tool registration and execution

## Phase 3: MCP SDK Migration 🎯 CURRENT (v0.2.0)

### Task 3.1: SDK Installation & Setup
**Description**: Install official MCP SDK and understand its structure
- [ ] Add `mcp` to project dependencies
- [ ] Study SDK documentation and examples
- [ ] Understand SDK server lifecycle
- [ ] Review transport options (stdio, SSE, WebSocket)
- [ ] Plan migration strategy

### Task 3.2: Server Wrapper Implementation
**Description**: Create MCP server using official SDK
- [ ] Create `app/mcp_server.py` with SDK Server
- [ ] Implement `@server.list_tools()` handler
- [ ] Implement `@server.call_tool()` handler
- [ ] Connect handlers to existing tool registry
- [ ] Add proper error handling with SDK types

### Task 3.3: Tool Schema Conversion
**Description**: Convert tool schemas to SDK format
- [ ] Adapt tool registry to return SDK Tool types
- [ ] Convert parameter schemas to `inputSchema` format
- [ ] Update tool metadata for SDK compatibility
- [ ] Test tool discovery with SDK
- [ ] Validate against MCP spec

### Task 3.4: Tool Execution Integration
**Description**: Connect SDK tool execution to existing logic
- [ ] Map SDK tool calls to registry execution
- [ ] Convert SDK arguments to tool parameters
- [ ] Format tool results as SDK TextContent
- [ ] Handle tool execution errors with SDK error types
- [ ] Test end-to-end execution flow

### Task 3.5: Transport Implementation
**Description**: Add multiple transport support
- [ ] Implement stdio transport for CLI/Agent use
- [ ] Add SSE transport for web clients
- [ ] Create HTTP adapter for REST compatibility (optional)
- [ ] Test each transport independently
- [ ] Document transport usage

### Task 3.6: Remove Legacy Code
**Description**: Clean up custom FastAPI implementation
- [ ] Remove `app/api/mcp.py` (custom REST endpoints)
- [ ] Remove custom protocol models (use SDK types)
- [ ] Update imports across the project
- [ ] Remove unused dependencies
- [ ] Clean up configuration for SDK

### Task 3.7: Update Entry Points
**Description**: Change application startup for SDK
- [ ] Update `run.py` to start MCP server
- [ ] Add command-line arguments for transport selection
- [ ] Create separate entry points (stdio, SSE, HTTP)
- [ ] Update development workflow documentation
- [ ] Test all entry points

### Task 3.8: Documentation Update
**Description**: Update all docs for SDK usage
- [ ] Update README with new installation steps
- [ ] Document stdio usage with AI agents
- [ ] Add Claude Desktop configuration example
- [ ] Update API documentation
- [ ] Create migration guide from v0.1.0

### Task 3.9: SDK Migration Testing
**Description**: Comprehensive testing of SDK implementation
- [ ] Test tool discovery via stdio
- [ ] Test tool execution via stdio
- [ ] Test with Claude Desktop integration
- [ ] Test with Google ADK (if HTTP adapter)
- [ ] Validate MCP protocol compliance

### Task 3.10: Release v0.2.0
**Description**: Package and release SDK-based version
- [ ] Update version to 0.2.0
- [ ] Create comprehensive changelog
- [ ] Tag release in Git
- [ ] Update GitHub release notes
- [ ] Announce breaking changes from v0.1.0

## Phase 4: Advanced Tool Development (v0.3.0)

### Task 4.1: Multi-Document Processing
**Description**: Handle batch processing of multiple PDFs
- [ ] Design batch processing tool schema
- [ ] Implement parallel document processing
- [ ] Add progress tracking for batches
- [ ] Handle partial failures gracefully
- [ ] Test with multiple documents

### Task 4.2: Tool Composition
**Description**: Enable chaining multiple tools
- [ ] Design tool composition patterns
- [ ] Implement pipeline tool (pdf → markdown → filter)
- [ ] Add intermediate result caching
- [ ] Handle errors in tool chains
- [ ] Test complex workflows

### Task 4.3: Advanced Chunking
**Description**: Smarter document splitting strategies
- [ ] Implement semantic chunking (by section/topic)
- [ ] Add chunk overlap optimization
- [ ] Create context preservation across chunks
- [ ] Implement chunk reassembly with coherence
- [ ] Test with various document structures

### Task 4.4: Result Optimization
**Description**: Improve output quality and performance
- [ ] Implement response caching for duplicate content
- [ ] Add prompt optimization based on document type
- [ ] Create quality metrics for tool outputs
- [ ] Implement A/B testing for prompts
- [ ] Benchmark performance improvements

## Phase 5: Production & Monitoring (v0.4.0)

### Task 5.1: Resource Management
**Description**: Add MCP resources support
- [ ] Implement prompt templates as resources
- [ ] Add document templates
- [ ] Create resource discovery endpoint
- [ ] Test resource access from clients
- [ ] Document resource usage

### Task 5.2: Monitoring & Metrics
**Description**: Add observability to MCP server
- [ ] Implement request/response logging
- [ ] Add execution time metrics
- [ ] Create health check endpoints
- [ ] Set up error tracking
- [ ] Add performance dashboards

### Task 5.3: Docker Deployment
**Description**: Containerize the application
- [ ] Create Dockerfile for MCP server
- [ ] Add docker-compose for development
- [ ] Configure environment variables
- [ ] Test container deployment
- [ ] Create deployment documentation

### Task 5.4: Performance Optimization
**Description**: Optimize for production load
- [ ] Implement connection pooling for Gemini API
- [ ] Add request queuing and rate limiting
- [ ] Optimize memory usage for large PDFs
- [ ] Implement graceful shutdown
- [ ] Load test and benchmark

### Task 5.5: Comprehensive Testing
**Description**: Full test coverage
- [ ] Unit tests for all tools
- [ ] Integration tests for SDK server
- [ ] End-to-end workflow tests
- [ ] Performance and load tests
- [ ] MCP protocol compliance tests

### Task 5.6: Production Documentation
**Description**: Complete documentation for production use
- [ ] Deployment guide
- [ ] Scaling recommendations
- [ ] Troubleshooting guide
- [ ] API reference with examples
- [ ] Contributing guidelines

