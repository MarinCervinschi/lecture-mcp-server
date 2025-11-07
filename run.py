import asyncio
import logging
import sys

from app.core.config import settings
from app.core.logging import setup_logging
from app.mcp_server import run_sse_server, run_stdio_server

setup_logging()
logger = logging.getLogger(__name__)


async def main() -> None:
    transport = settings.TRANSPORT.lower()
    try:
        if transport == "stdio":
            await run_stdio_server()
        elif transport == "sse":
            await run_sse_server()
        else:
            logger.error(f"Unknown transport: {transport}")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\nServer shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
