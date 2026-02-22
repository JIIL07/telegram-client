from __future__ import annotations

from telethon import TelegramClient

from config import settings


def build_client() -> TelegramClient:
    return TelegramClient(
        settings.session_name,
        settings.api_id,
        settings.api_hash,
    )
