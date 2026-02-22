from __future__ import annotations

import logging

from telethon import TelegramClient, events

from api import forward_message_to_myaso
from db import get_client_send_permission
from handlers.outgoing import normalize_phone

logger = logging.getLogger(__name__)


def register_incoming_handlers(client: TelegramClient) -> None:
    @client.on(events.NewMessage(incoming=True))
    async def on_incoming_message(event: events.NewMessage.Event) -> None:
        text = (event.raw_text or "").strip()
        if not text:
            logger.debug("Incoming message without text. Skip.")
            return

        sender = await event.get_sender()
        if sender is None:
            logger.warning("Cannot resolve sender for message id=%s", event.id)
            return

        sender_phone = getattr(sender, "phone", None)
        if not sender_phone:
            logger.info(
                "Incoming sender has no phone (id=%s). "
                "Phone-only mode enabled, skipping.",
                getattr(sender, "id", "unknown"),
            )
            return

        normalized_phone = normalize_phone(sender_phone)
        exists, can_send = await get_client_send_permission(normalized_phone)

        if not exists:
            logger.info("Client not found in DB: %s. Skip.", normalized_phone)
            return

        if not can_send:
            logger.info("Client blocked by send_message=false: %s", normalized_phone)
            return

        try:
            response = await forward_message_to_myaso(normalized_phone, text)
            logger.info(
                "Forwarded incoming message to myaso API. phone=%s response=%s",
                normalized_phone,
                response,
            )
        except Exception:
            logger.exception(
                "Failed to forward message to myaso API. phone=%s",
                normalized_phone,
            )
