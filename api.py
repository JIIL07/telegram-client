from __future__ import annotations

import httpx

from config import settings


async def forward_message_to_myaso(phone: str, message: str) -> dict:
    payload = {
        "phone": phone,
        "message": message,
    }
    timeout = httpx.Timeout(settings.myaso_api_timeout_seconds)
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(settings.myaso_forward_url, json=payload)
        response.raise_for_status()
        return response.json()
