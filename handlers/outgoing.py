from __future__ import annotations

import re
from typing import Any

from telethon import TelegramClient, events

PHONE_PATTERN = re.compile(r"^\+?[0-9][0-9\-\s\(\)]{8,}$")


def normalize_phone(phone: str) -> str:
    value = (
        phone.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    if value.startswith("8") and len(value) > 1:
        value = "+7" + value[1:]
    elif value.startswith("7") and len(value) > 1 and not value.startswith("+"):
        value = "+" + value
    elif not value.startswith("+"):
        if value.startswith("9") and len(value) == 10:
            value = "+7" + value
        else:
            value = "+" + value
    return value


def resolve_entity(recipient: str) -> str | int:
    recipient = recipient.strip()
    if not recipient:
        raise ValueError("Recipient is empty.")

    if recipient.startswith("@"):
        return recipient

    if PHONE_PATTERN.match(recipient):
        return normalize_phone(recipient)

    if recipient.isdigit():
        return int(recipient)

    return recipient


async def send_text_message(client: TelegramClient, recipient: str, text: str) -> Any:
    entity = resolve_entity(recipient)
    return await client.send_message(entity, text)


async def send_file_from_url(
    client: TelegramClient,
    recipient: str,
    file_url: str,
    caption: str | None = None,
) -> Any:
    entity = resolve_entity(recipient)
    return await client.send_file(entity, file_url, caption=caption or "")


def register_outgoing_handlers(client: TelegramClient) -> None:
    @client.on(events.NewMessage(outgoing=True, pattern=r"(?is)^/send\s+(\S+)\s+(.+)$"))
    async def cmd_send(event: events.NewMessage.Event) -> None:
        recipient = event.pattern_match.group(1)
        text = event.pattern_match.group(2).strip()
        if not text:
            await event.reply("Text is required. Usage: /send <recipient> <text>")
            return
        try:
            sent = await send_text_message(client, recipient, text)
            await event.reply(f"Message sent. id={sent.id}")
        except Exception as exc:
            await event.reply(f"Send error: {exc}")

    @client.on(
        events.NewMessage(
            outgoing=True,
            pattern=r"(?is)^/send_file\s+(\S+)\s+(\S+)(?:\s+(.+))?$",
        )
    )
    async def cmd_send_file(event: events.NewMessage.Event) -> None:
        recipient = event.pattern_match.group(1)
        file_url = event.pattern_match.group(2)
        caption = event.pattern_match.group(3) or ""
        try:
            sent = await send_file_from_url(client, recipient, file_url, caption=caption)
            await event.reply(f"File sent. id={sent.id}")
        except Exception as exc:
            await event.reply(f"Send file error: {exc}")
