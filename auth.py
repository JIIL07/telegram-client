from __future__ import annotations

import asyncio
from getpass import getpass

from telethon.errors import SessionPasswordNeededError

from client import build_client


async def run_auth() -> None:
    client = build_client()
    await client.connect()

    try:
        if await client.is_user_authorized():
            print("Session already authorized.")
            return

        phone = input("Enter Telegram phone (example: +79991234567): ").strip()
        if not phone:
            raise RuntimeError("Phone number is required.")

        await client.send_code_request(phone)
        code = input("Enter code from Telegram: ").strip()
        if not code:
            raise RuntimeError("Login code is required.")

        try:
            await client.sign_in(phone=phone, code=code)
        except SessionPasswordNeededError:
            password = getpass("Enter Telegram 2FA password: ").strip()
            if not password:
                raise RuntimeError("2FA password is required.")
            await client.sign_in(password=password)

        me = await client.get_me()
        print(f"Authorized successfully as: id={me.id}")
    finally:
        await client.disconnect()


if __name__ == "__main__":
    asyncio.run(run_auth())
