import logging
from contextlib import asynccontextmanager
from typing import Any

from mcp.server import Server
from mcp.types import Tool

from app.core.config import settings
from app.services.mcp_registry import get_mcp_registry

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: Server):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")

    yield

    # Shutdown
    logger.info(f"Shutting down {settings.PROJECT_NAME}")


async def create_server() -> Server:
    """Create and configure the MCP server instance."""

    registry = get_mcp_registry()
    server = Server(
        name=settings.PROJECT_NAME,
        version=settings.VERSION,
        lifespan=lifespan,
    )

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return registry.list_tools()

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> Any:
        """Execute tool - clean integration!"""
        try:
            result = await registry.execute_tool(name, arguments)
            return result
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
    from mcp.server.sse import SseServerTransport
    from starlette.applications import Starlette
    from starlette.requests import Request
    from starlette.routing import Route

    host: str = settings.HOST
    port: int = settings.PORT

    logger.info("Starting MCP server with SSE transport")
    logger.info(f"Server: {settings.PROJECT_NAME} v{settings.VERSION}")

    server = await create_server()
    sse = SseServerTransport("/mcp")

    async def handle_sse(request: Request):
        """Handle SSE connection."""
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )

    async def handle_messages(request: Request):
        """Handle POST messages."""
        await sse.handle_post_message(request.scope, request.receive, request._send)

    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/mcp", endpoint=handle_messages, methods=["POST"]),
        ]
    )

    import uvicorn

    config = uvicorn.Config(
        app,
        host=host,
        port=port,
        log_level=settings.LOG_LEVEL.lower(),
        reload=settings.is_development,
        workers=settings.WORKERS,
    )
    server_instance = uvicorn.Server(config)
    await server_instance.serve()
