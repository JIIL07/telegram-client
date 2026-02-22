from __future__ import annotations

import asyncio
from typing import Optional

import asyncpg

from config import settings

_pool: Optional[asyncpg.Pool] = None
_lock = asyncio.Lock()


async def get_pool() -> asyncpg.Pool:
    global _pool

    if _pool is not None:
        return _pool

    async with _lock:
        if _pool is None:
            _pool = await asyncpg.create_pool(
                dsn=settings.postgres_dsn,
                min_size=1,
                max_size=5,
                command_timeout=20.0,
            )

    return _pool


async def close_pool() -> None:
    global _pool

    if _pool is not None:
        await _pool.close()
        _pool = None


async def get_client_send_permission(phone: str) -> tuple[bool, bool]:
    pool = await get_pool()
    query = """
        SELECT send_message
        FROM myaso.clients
        WHERE phone = $1
        LIMIT 1
    """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(query, phone)

    if row is None:
        return False, False

    send_message = row["send_message"]
    return True, bool(send_message) if send_message is not None else True
