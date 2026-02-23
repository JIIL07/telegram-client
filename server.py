from __future__ import annotations

import logging
from typing import Any

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from telethon import TelegramClient

from handlers.outgoing import resolve_entity, send_file_from_url, send_text_message

logger = logging.getLogger(__name__)

app = FastAPI(title="telegram-client")


def create_app(client: TelegramClient) -> FastAPI:
    app.state.client = client
    return app


class SendMessageRequest(BaseModel):
    recipient: str
    text: str


@app.post("/send-message")
async def send_message(req: SendMessageRequest) -> dict[str, Any]:
    client: TelegramClient = app.state.client
    try:
        sent = await send_text_message(client, req.recipient, req.text)
        return {"ok": True, "message_id": sent.id}
    except Exception as exc:
        logger.exception("Send message failed: recipient=%s", req.recipient)
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/send-file")
async def send_file(
    recipient: str = Form(...),
    file: UploadFile | None = File(default=None),
    file_url: str | None = Form(default=None),
    caption: str | None = Form(default=None),
) -> dict[str, Any]:
    client: TelegramClient = app.state.client

    if file_url:
        try:
            sent = await send_file_from_url(
                client, recipient, file_url, caption=caption or ""
            )
            return {"ok": True, "message_id": sent.id}
        except Exception as exc:
            logger.exception("Send file from URL failed: recipient=%s", recipient)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    if file:
        try:
            data = await file.read()
            entity = resolve_entity(recipient)
            sent = await client.send_file(entity, data, caption=caption or "")
            return {"ok": True, "message_id": sent.id}
        except Exception as exc:
            logger.exception("Send file upload failed: recipient=%s", recipient)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    raise HTTPException(
        status_code=400,
        detail="Provide either 'file' (upload) or 'file_url' (form field)",
    )
