import asyncio
import os

from dotenv import load_dotenv

from connectors.telegram import TelegramConnector
from infrastructure.container import build_process_reel_service

load_dotenv()


async def run() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN must be set")

    authorized_user_ids = os.getenv("TELEGRAM_AUTHORIZED_USER_IDS", "")
    user_ids = (
        [int(uid) for uid in authorized_user_ids.split(",") if uid.strip()]
        if authorized_user_ids
        else []
    )

    service = build_process_reel_service()
    connector = TelegramConnector(
        service=service, token=token, authorized_user_ids=user_ids
    )
    await connector.run()


if __name__ == "__main__":
    asyncio.run(run())
