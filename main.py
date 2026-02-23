from __future__ import annotations

import asyncio
import logging

import uvicorn

from client import build_client
from config import settings
from db import close_pool
from handlers import register_incoming_handlers, register_outgoing_handlers
from server import create_app


def setup_logging() -> None:
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


async def run() -> None:
    setup_logging()
    logger = logging.getLogger(__name__)

    client = build_client()
    register_outgoing_handlers(client)
    register_incoming_handlers(client)

    logger.info("Starting telegram-client with session=%s", settings.session_name)
    await client.start()

    app = create_app(client)
    config = uvicorn.Config(app, host=settings.host, port=settings.port)
    server = uvicorn.Server(config)
    server_task = asyncio.create_task(server.serve())
    logger.info("Web server listening on %s:%s", settings.host, settings.port)

    try:
        await client.run_until_disconnected()
    finally:
        server_task.cancel()
        try:
            await server_task
        except asyncio.CancelledError:
            pass
        await close_pool()
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(run())
