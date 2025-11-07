import asyncio
import logging
import sys

import click

from app.core.logging import setup_logging
from app.mcp_server import run_sse_server, run_stdio_server

setup_logging()
logger = logging.getLogger(__name__)


@click.command()
@click.option(
    "--transport",
    type=click.Choice(["sse", "stdio"], case_sensitive=False),
    default="sse",
    help="Transport method for the MCP server (sse or stdio). Default is sse.",
)
def main(transport: str) -> None:
    async def run_app():
        try:
            if transport == "sse":
                await run_sse_server()
            elif transport == "stdio":
                await run_stdio_server()

        except KeyboardInterrupt:
            logger.info("\nServer shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            sys.exit(1)

    asyncio.run(run_app())


if __name__ == "__main__":
    main()
