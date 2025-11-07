import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, Dict

import uvicorn
from mcp.server.lowlevel import Server
from mcp.types import Tool

from app.core.config import settings
from app.services.mcp_registry import get_mcp_registry

logger = logging.getLogger(__name__)


async def create_server() -> Server:
    """Create and configure the MCP server instance."""

    registry = get_mcp_registry()
    server = Server(
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
    )

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return registry.list_tools()

    @server.call_tool()
    async def call_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool"""
        try:
            return await registry.execute_tool(name, args)
        except ValueError as e:
            raise ValueError(f"Tool '{name}' not found: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Execution failed: {str(e)}")

    return server


async def run_stdio_server():
    """Run MCP server with stdio transport (for Claude Desktop)."""
    from mcp.server.stdio import stdio_server

    logger.info("Starting MCP server with STDIO transport")
    logger.info(f"Server: {settings.PROJECT_NAME} v{settings.VERSION}")

    server = await create_server()

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream, write_stream, server.create_initialization_options()
        )


async def run_sse_server():
    """Run MCP server with SSE transport (for web apps)."""
    from mcp.server.streamable_http_manager import StreamableHTTPSessionManager
    from starlette.applications import Starlette
    from starlette.middleware.cors import CORSMiddleware
    from starlette.routing import Mount
    from starlette.types import Receive, Scope, Send

    server = await create_server()

    session_manager = StreamableHTTPSessionManager(
        app=server, event_store=None, stateless=True
    )

    @asynccontextmanager
    async def lifespan(_: Starlette) -> AsyncIterator[None]:
        """Context manager for session manager."""
        async with session_manager.run():
            try:
                yield
            finally:
                logger.info("Application shutting down...")

    async def handle_streamable_http(
        scope: Scope, receive: Receive, send: Send
    ) -> None:
        await session_manager.handle_request(scope, receive, send)

    app = Starlette(
        routes=[
            Mount("/mcp", app=handle_streamable_http),
        ],
        lifespan=lifespan,
    )

    app = CORSMiddleware(
        app,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "DELETE"],
        expose_headers=["Mcp-Session-Id"],
    )

    config = uvicorn.Config(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL.lower(),
    )
    server = uvicorn.Server(config)
    await server.serve()
